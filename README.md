# Model Explanation Consistency Agent

A deterministic local checker for prediction and explanation record consistency.

## Capabilities
- Validate required prediction/explanation fields.
- Detect duplicate IDs and missing counterpart records.
- Check feature-name list consistency.
- Check numeric attribution values.
- Compare prediction labels when configured.
- Write a JSON report with stable rule IDs.

## Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python verification/readiness_audit.py
```

## Run the demo
```bash
python -m core.cli validate examples/predictions.csv examples/explanations.csv --config examples/config.json --output explanation-report.json
```

The sample files intentionally include mismatches to demonstrate findings. Review the report; detected inconsistencies are expected for the demo.

## Limitations
The agent checks supplied records only. It cannot prove that explanations are faithful to a model or establish causality.
