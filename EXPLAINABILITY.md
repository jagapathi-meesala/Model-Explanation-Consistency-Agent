# Explainability and Decision Record

## Purpose
The Model Explanation Consistency Agent checks local prediction and explanation records for structural consistency and selected cross-record mismatches. It reports evidence-backed findings to help reviewers investigate explanation pipeline issues.

## Decision and Reasoning
The agent applies deterministic checks to the supplied CSV files and optional JSON configuration. It checks required fields, duplicate IDs, missing explanation records, feature-name consistency, numeric attribution values, and prediction-label agreement when configured columns are available. Each finding includes a stable rule ID, severity, a concise reason, and record identifiers or row numbers when possible. These checks identify data inconsistencies and do not prove that an explanation faithfully represents a model.

## Inputs and Data Sources
The agent accepts local CSV files containing prediction records and explanation records, plus an optional JSON configuration that maps record ID, prediction label, feature names, attribution values, and expected fields. The user-provided files are the only data sources. The agent does not call model APIs, retrieve external data, or inspect hidden model internals.

## Limits and Known Issues
The agent cannot establish causal validity, fairness, model correctness, or explanation faithfulness from tabular records alone. It cannot reproduce predictions unless the model and inference pipeline are separately supplied and configured, which this version does not execute. Feature names may need normalization upstream if different pipelines use aliases. Missing or incorrect configuration can limit which comparisons are possible.

## Outputs and Evidence
The JSON report contains status, files inspected, checks executed, severity counts, findings, and limitations. Findings include stable rule identifiers and record IDs or row numbers when available. The report is intended for investigation and is not an automatic model or compliance approval.

## Severity and Prioritization
Errors include duplicate configured IDs, missing required fields, and invalid attribution values. Warnings include prediction records without explanations, explanations without predictions, feature-name differences, and prediction-label disagreements. Informational findings summarize completed checks. A warning indicates a condition to review and does not by itself prove the model or explanation is wrong.

## Human Review
A qualified ML reviewer should evaluate explanation method assumptions, model version alignment, feature preprocessing, attribution semantics, and whether the explanation is appropriate for the decision context. Reviewers should use model-specific tests before making claims about faithfulness or safety.

## Safety and Data Handling
The agent processes supplied files locally and does not access external services. Reports avoid reproducing full record contents by default. Users should remove personal data, secrets, and restricted fields before sharing files.

## Non-Goals
The agent does not train models, generate explanations, modify predictions, prove causality, certify model behavior, or replace model-specific validation and human review.
