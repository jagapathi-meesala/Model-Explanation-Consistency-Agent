from pathlib import Path
import re, sys
root=Path(__file__).resolve().parents[1]
required=["agent.yaml","SOUL.md","AGENTS.md","RULES.md","DUTIES.md","EXPLAINABILITY.md","README.md","requirements.txt","core/engine.py","core/cli.py","tools/validate-explanation-records.yaml","tools/audit-attribution-consistency.yaml","tools/compare-prediction-explanations.yaml","skills/explanation-record-validation/SKILL.md","skills/attribution-consistency-audit/SKILL.md","skills/prediction-explanation-comparison/SKILL.md","tests/test_engine.py","examples/predictions.csv","examples/explanations.csv","examples/config.json","contracts/explanation-config.schema.json"]
missing=[x for x in required if not (root/x).is_file()]
manifest=(root/"agent.yaml").read_text()
explain=(root/"EXPLAINABILITY.md").read_text()
name_ok=bool(re.search(r"(?m)^name: [a-z][a-z0-9]*(?:-[a-z0-9]+)*$",manifest))
headings=all(re.search(rf"(?im)^## .*\b{w}\b",explain) for w in ["Decision","Inputs","Limits"])
print(f"Required files: {len(required)-len(missing)}/{len(required)}")
if missing: print("Missing:",missing)
print("Agent name valid:", "PASS" if name_ok else "FAIL")
print("Explainability headings:", "PASS" if headings else "FAIL")
sys.exit(bool(missing or not name_ok or not headings))
