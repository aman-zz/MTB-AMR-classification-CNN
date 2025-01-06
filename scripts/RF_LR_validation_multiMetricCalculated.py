import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate
from sklearn.metrics import confusion_matrix, make_scorer
from sklearn.preprocessing import StandardScaler

# List of drugs
drugL = ["ethambutol", "isoniazid", "pyrazinamide", "rifampicin"]


# Define custom scoring functions
def tn(y_true, y_pred):
    return confusion_matrix(y_true, y_pred)[0, 0]

def fp(y_true, y_pred):
    return confusion_matrix(y_true, y_pred)[0, 1]

def fn(y_true, y_pred):
    return confusion_matrix(y_true, y_pred)[1, 0]

def tp(y_true, y_pred):
    return confusion_matrix(y_true, y_pred)[1, 1]

# Define scoring metrics
scoring = {
    "tp": make_scorer(tp),
    "tn": make_scorer(tn),
    "fp": make_scorer(fp),
    "fn": make_scorer(fn),
}

def evaluate_model(model, X, y, scoring, cv=3):
    """
    Evaluate a model using cross-validation and return calculated metrics.
    """
    results = cross_validate(model, X, y, scoring=scoring, cv=cv)

    s_tn = sum(results["test_tn"])
    s_tp = sum(results["test_tp"])
    s_fn = sum(results["test_fn"])
    s_fp = sum(results["test_fp"])

    metrics = {
        "tp": s_tp,
        "tn": s_tn,
        "fp": s_fp,
        "fn": s_fn,
        "accuracy": (s_tp + s_tn) / float(s_tp + s_tn + s_fp + s_fn),
        "specificity": s_tn / float(s_tn + s_fp),
        "sensitivity": s_tp / float(s_tp + s_fn),
        "precision": s_tp / float(s_tp + s_fp),
    }

    metrics["f_measure"] = 2 * (metrics["sensitivity"] * metrics["precision"]) / (
        metrics["sensitivity"] + metrics["precision"]
    )

    return metrics

def save_model(model, filename):
    """
    Save the trained model to a file for reuse.
    """
    joblib.dump(model, filename)

# Process data and evaluate models for each drug
for drug in drugL:
    print(f"Evaluating models for drug: {drug}")

    # Load feature matrix and labels
    X = np.loadtxt(f"featureM_X_{drug}.txt", dtype="i4")
    y = np.loadtxt(f"label_Y_{drug}.txt", dtype="i4")

    # Standardize features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Define models
    rf_model = RandomForestClassifier(n_estimators=1000, random_state=0, n_jobs=-1)
    lr_model = LogisticRegression(n_jobs=-1, penalty="l2", random_state=0)

    # Train and save Random Forest model
    rf_model.fit(X, y)
    save_model(rf_model, f"random_forest_{drug}.joblib")

    # Evaluate Random Forest
    rf_metrics = evaluate_model(rf_model, X, y, scoring)
    print("Random Forest Results:")
    for metric, value in rf_metrics.items():
        print(f"{metric}: {value:.4f}")

    # Train and save Logistic Regression model
    lr_model.fit(X, y)
    save_model(lr_model, f"logistic_regression_{drug}.joblib")

    # Evaluate Logistic Regression
    lr_metrics = evaluate_model(lr_model, X, y, scoring)
    print("Logistic Regression Results:")
    for metric, value in lr_metrics.items():
        print(f"{metric}: {value:.4f}")

    print("\n")
