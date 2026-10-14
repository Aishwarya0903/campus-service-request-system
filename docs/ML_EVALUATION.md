# ML evaluation

Run `python ml/training/train_models.py` to generate this project's actual metrics. The script writes a machine-readable report to `ml/models/evaluation.json`; this repository intentionally does not pre-state metric values because they must come from the local run.

The category and priority experiments compare TF-IDF plus Logistic Regression against TF-IDF plus Linear SVM. Reported measures are validation accuracy, macro-F1, and confusion matrices. The selected artifact uses the candidate with the best held-out macro-F1.

The SLA experiment trains Gradient Boosting on synthetic operational history. Inputs are elapsed hours, category, priority, created hour, day of week, and workload. Its validation metrics characterize only generated data and are **not yet evaluated** against real campus history. AUC-ROC and alert-budget precision on genuine historical data remain Final Review 3 work.
