import csv, json
from pathlib import Path

def load_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"CSV must contain a header row: {path}")
        return list(reader.fieldnames), list(reader)

def load_config(path):
    if not path:
        return {}
    with open(path, encoding="utf-8") as f:
        value = json.load(f)
    if not isinstance(value, dict):
        raise ValueError("Configuration must be a JSON object")
    return value

def finding(rule_id, severity, message, **extra):
    return {"rule_id": rule_id, "severity": severity, "message": message, **extra}

def _split_names(value):
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed]
    except (json.JSONDecodeError, TypeError):
        pass
    return [x.strip() for x in str(value).split(";") if x.strip()]

def _split_numbers(value):
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    return [x.strip() for x in str(value).split(";") if x.strip()]

def validate_records(prediction_path, explanation_path, config_path=None):
    config = load_config(config_path)
    pred_cols, predictions = load_csv(prediction_path)
    exp_cols, explanations = load_csv(explanation_path)
    findings = []
    id_col = config.get("id_column", "record_id")
    pred_label = config.get("prediction_label_column", "prediction")
    exp_label = config.get("explanation_label_column", "prediction")
    features_col = config.get("feature_names_column", "feature_names")
    attrs_col = config.get("attributions_column", "attributions")
    required_pred = config.get("required_prediction_columns", [id_col, pred_label])
    required_exp = config.get("required_explanation_columns", [id_col, features_col, attrs_col])

    for col in required_pred:
        if col not in pred_cols:
            findings.append(finding("MEC001","error",f"Required prediction column is missing: {col}",column=col))
    for col in required_exp:
        if col not in exp_cols:
            findings.append(finding("MEC002","error",f"Required explanation column is missing: {col}",column=col))

    if id_col in pred_cols and id_col in exp_cols:
        pred_ids = {}
        exp_ids = {}
        for i, row in enumerate(predictions, start=2):
            rid = (row.get(id_col) or "").strip()
            if rid:
                pred_ids.setdefault(rid, []).append(i)
        for i, row in enumerate(explanations, start=2):
            rid = (row.get(id_col) or "").strip()
            if rid:
                exp_ids.setdefault(rid, []).append(i)
        dup_pred = {k:v for k,v in pred_ids.items() if len(v)>1}
        dup_exp = {k:v for k,v in exp_ids.items() if len(v)>1}
        if dup_pred:
            findings.append(finding("MEC003","error","Duplicate prediction record IDs detected",record_ids=sorted(dup_pred),csv_rows=[n for v in dup_pred.values() for n in v][:20]))
        if dup_exp:
            findings.append(finding("MEC004","error","Duplicate explanation record IDs detected",record_ids=sorted(dup_exp),csv_rows=[n for v in dup_exp.values() for n in v][:20]))
        pset, eset = set(pred_ids), set(exp_ids)
        if pset - eset:
            findings.append(finding("MEC005","warning","Prediction records have no matching explanation record",record_ids=sorted(pset-eset)[:50]))
        if eset - pset:
            findings.append(finding("MEC006","warning","Explanation records have no matching prediction record",record_ids=sorted(eset-pset)[:50]))
        if pred_label in pred_cols and exp_label in exp_cols and config.get("require_matching_prediction_label", True):
            disagreements = []
            for rid in sorted(pset & eset):
                if len(pred_ids[rid]) == 1 and len(exp_ids[rid]) == 1:
                    prow, erow = predictions[pred_ids[rid][0]-2], explanations[exp_ids[rid][0]-2]
                    if (prow.get(pred_label) or "").strip() != (erow.get(exp_label) or "").strip():
                        disagreements.append(rid)
            if disagreements:
                findings.append(finding("MEC007","warning","Prediction labels differ between prediction and explanation records",record_ids=disagreements[:50]))

    if features_col in exp_cols and attrs_col in exp_cols:
        bad_features, bad_attributions, length_mismatch = [], [], []
        for i, row in enumerate(explanations, start=2):
            names = _split_names(row.get(features_col, ""))
            values = _split_numbers(row.get(attrs_col, ""))
            if not names:
                bad_features.append(i)
            if not values:
                bad_attributions.append(i)
            numeric = True
            for val in values:
                try:
                    float(val)
                except (ValueError, TypeError):
                    numeric = False
                    break
            if values and not numeric:
                bad_attributions.append(i)
            if names and values and len(names) != len(values):
                length_mismatch.append(i)
        if bad_features:
            findings.append(finding("MEC008","warning","Feature-name list is empty or unreadable",csv_rows=bad_features[:20]))
        if bad_attributions:
            findings.append(finding("MEC009","error","Attribution values are missing or contain non-numeric entries",csv_rows=sorted(set(bad_attributions))[:20]))
        if length_mismatch:
            findings.append(finding("MEC010","error","Feature-name and attribution counts differ",csv_rows=length_mismatch[:20]))

    findings.append(finding("MEC000","info","Prediction and explanation files inspected",prediction_file=Path(prediction_path).name,explanation_file=Path(explanation_path).name,prediction_rows=len(predictions),explanation_rows=len(explanations)))
    status = "error" if any(x["severity"]=="error" for x in findings) else "warning" if any(x["severity"]=="warning" for x in findings) else "ok"
    return {
      "status": status,
      "files_inspected": [str(prediction_path), str(explanation_path)] + ([str(config_path)] if config_path else []),
      "checks_executed": ["required_columns","duplicate_ids","counterpart_records","prediction_label_agreement","feature_attribution_consistency"],
      "severity_counts": {s:sum(x["severity"]==s for x in findings) for s in ("error","warning","info")},
      "findings": findings,
      "limitations": ["Checks cover supplied records only.", "Structural consistency does not prove explanation faithfulness, causal validity, or model correctness."]
    }
