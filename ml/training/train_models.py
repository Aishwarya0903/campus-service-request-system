"""Generate clearly labelled synthetic campus data and train reproducible ML artifacts."""

from pathlib import Path
import json
import random

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    roc_auc_score,
)


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "ml" / "data"
MODELS = ROOT / "ml" / "models"

random.seed(42)


templates = {
    "Electrical": [
        "light is not working in {place}",
        "fan has stopped in {place}",
        "sparks from power socket near {place}",
        "corridor lights are damaged at {place}",
    ],
    "Plumbing": [
        "water is leaking from tap in {place}",
        "washroom drain is blocked in {place}",
        "broken pipe is flooding {place}",
        "there is no water supply in {place}",
    ],
    "IT/Network": [
        "wifi is not connecting in {place}",
        "internet keeps disconnecting at {place}",
        "computer will not start in {place}",
        "projector network connection failed in {place}",
    ],
    "Hostel": [
        "broken bed frame in {place}",
        "room door lock is damaged in {place}",
        "hostel furniture needs repair in {place}",
        "hostel room maintenance required in {place}",
    ],
}


places = [
    "hostel block A",
    "hostel block B",
    "classroom 204",
    "library",
    "lab 3",
    "ground floor corridor",
    "washroom",
    "room 312",
]


def priority(text):
    if any(
        x in text
        for x in [
            "sparks",
            "flooding",
            "no water",
            "will not start",
        ]
    ):
        return "HIGH"

    if any(
        x in text
        for x in [
            "damaged",
            "blocked",
            "failed",
            "broken",
        ]
    ):
        return "MEDIUM"

    return "LOW"


# ---------------------------------------------------------
# 1. Generate synthetic campus ticket dataset
# ---------------------------------------------------------

rows = []

for category, items in templates.items():
    for _ in range(100):
        text = random.choice(items).format(
            place=random.choice(places)
        )

        rows.append(
            {
                "text": text,
                "category": category,
                "priority": priority(text),
            }
        )


df = pd.DataFrame(rows)

DATA.mkdir(exist_ok=True)

df.to_csv(
    DATA / "synthetic_campus_tickets.csv",
    index=False,
)


# ---------------------------------------------------------
# 2. Train category and priority models
# ---------------------------------------------------------

tr, te = train_test_split(
    df,
    test_size=0.25,
    random_state=42,
    stratify=df.category,
)


def choose(label):

    candidates = {
        "logistic_regression": Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        stop_words="english",
                        ngram_range=(1, 2),
                    ),
                ),
                (
                    "model",
                    LogisticRegression(
                        max_iter=2000,
                        random_state=42,
                    ),
                ),
            ]
        ),
        "linear_svm": Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        stop_words="english",
                        ngram_range=(1, 2),
                    ),
                ),
                (
                    "model",
                    LinearSVC(),
                ),
            ]
        ),
    }

    results = {}

    for name, model in candidates.items():

        model.fit(
            tr.text,
            tr[label],
        )

        predictions = model.predict(te.text)

        results[name] = {
            "accuracy": accuracy_score(
                te[label],
                predictions,
            ),
            "macro_f1": precision_recall_fscore_support(
                te[label],
                predictions,
                average="macro",
                zero_division=0,
            )[2],
            "confusion_matrix": confusion_matrix(
                te[label],
                predictions,
            ).tolist(),
        }

    best = max(
        results,
        key=lambda name: results[name]["macro_f1"],
    )

    candidates[best].fit(
        df.text,
        df[label],
    )

    return candidates[best], results, best


category_model, category_results, category_best = choose(
    "category"
)

priority_model, priority_results, priority_best = choose(
    "priority"
)


MODELS.mkdir(exist_ok=True)

joblib.dump(
    {
        "category": category_model,
        "priority": priority_model,
    },
    MODELS / "classifier.joblib",
)


# ---------------------------------------------------------
# 3. Generate synthetic operational SLA history
# ---------------------------------------------------------

op = []

for _ in range(1200):

    category = random.choice(
        list(templates)
    )

    priority_value = random.choices(
        ["LOW", "MEDIUM", "HIGH"],
        [0.3, 0.5, 0.2],
    )[0]

    elapsed = random.uniform(0, 72)
    workload = random.randint(0, 25)
    hour = random.randint(0, 23)
    day = random.randint(0, 6)

    base = (
        elapsed
        / {
            "Electrical": 24,
            "Plumbing": 24,
            "IT/Network": 12,
            "Hostel": 48,
        }[category]
        + {
            "LOW": 0,
            "MEDIUM": 0.25,
            "HIGH": 0.5,
        }[priority_value]
        + workload / 35
    )

    breach = int(
        base + random.uniform(-0.35, 0.35) > 1
    )

    op.append(
        [
            elapsed,
            category,
            priority_value,
            hour,
            day,
            workload,
            breach,
        ]
    )


operational_df = pd.DataFrame(
    op,
    columns=[
        "elapsed_hours",
        "category",
        "priority",
        "hour",
        "day_of_week",
        "workload",
        "breach",
    ],
)


operational_train, operational_test = train_test_split(
    operational_df,
    test_size=0.25,
    random_state=42,
    stratify=operational_df.breach,
)


# ---------------------------------------------------------
# 4. Train SLA Gradient Boosting model
# ---------------------------------------------------------

prep = ColumnTransformer(
    [
        (
            "categorical",
            __import__(
                "sklearn"
            ).preprocessing.OneHotEncoder(
                handle_unknown="ignore"
            ),
            ["category", "priority"],
        )
    ],
    remainder="passthrough",
)


sla_model = Pipeline(
    [
        (
            "prep",
            prep,
        ),
        (
            "model",
            GradientBoostingClassifier(
                random_state=42
            ),
        ),
    ]
)


sla_model.fit(
    operational_train.drop(
        columns="breach"
    ),
    operational_train.breach,
)


sla_predictions = sla_model.predict(
    operational_test.drop(
        columns="breach"
    )
)

sla_probabilities = sla_model.predict_proba(
    operational_test.drop(
        columns="breach"
    )
)[:, 1]


# ---------------------------------------------------------
# 5. SLA evaluation
# ---------------------------------------------------------

sla_accuracy = accuracy_score(
    operational_test.breach,
    sla_predictions,
)

sla_macro_f1 = precision_recall_fscore_support(
    operational_test.breach,
    sla_predictions,
    average="macro",
    zero_division=0,
)[2]

sla_confusion_matrix = confusion_matrix(
    operational_test.breach,
    sla_predictions,
).tolist()


# ROC-AUC
sla_auc = roc_auc_score(
    operational_test.breach,
    sla_probabilities,
)


# ---------------------------------------------------------
# 6. Precision at fixed alert budget
# ---------------------------------------------------------
# Alert the top 20% of tickets with the highest predicted
# breach probability.

alert_budget = 0.20

alert_count = max(
    1,
    int(
        len(sla_probabilities)
        * alert_budget
    ),
)

ranked_indices = sorted(
    range(len(sla_probabilities)),
    key=lambda i: sla_probabilities[i],
    reverse=True,
)

alert_indices = ranked_indices[:alert_count]

actual_breaches = operational_test.breach.to_numpy()

true_alerts = sum(
    actual_breaches[i] == 1
    for i in alert_indices
)

precision_at_alert_budget = (
    true_alerts / alert_count
)


# ---------------------------------------------------------
# 7. Save SLA model
# ---------------------------------------------------------

joblib.dump(
    sla_model,
    MODELS / "sla.joblib",
)


# ---------------------------------------------------------
# 8. Save complete evaluation report
# ---------------------------------------------------------

report = {
    "dataset": (
        "Synthetic campus-style data generated by this "
        "script; not real VIT data."
    ),
    "records": len(df),

    "category": {
        "selected": category_best,
        "candidates": category_results,
    },

    "priority": {
        "selected": priority_best,
        "candidates": priority_results,
    },

    "sla": {
        "model": "GradientBoostingClassifier",
        "synthetic_operational_records": len(
            operational_df
        ),
        "validation": {
            "accuracy": sla_accuracy,
            "macro_f1": sla_macro_f1,
            "roc_auc": sla_auc,
            "precision_at_alert_budget": (
                precision_at_alert_budget
            ),
            "alert_budget": alert_budget,
            "confusion_matrix": (
                sla_confusion_matrix
            ),
        },
    },
}


(
    MODELS / "evaluation.json"
).write_text(
    json.dumps(
        report,
        indent=2,
    )
)


print(
    json.dumps(
        report,
        indent=2,
    )
)