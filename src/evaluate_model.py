import json
import os

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    log_loss,
    brier_score_loss,
    confusion_matrix,
    classification_report
)


def evaluate_model(model, X_test, y_test, model_name="Model", save_path=None):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "model_name": model_name,
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_test, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_test, y_prob), 4),
        "log_loss": round(log_loss(y_test, y_prob), 4),
        "brier_score": round(brier_score_loss(y_test, y_prob), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(
            y_test,
            y_pred,
            zero_division=0,
            output_dict=True
        )
    }

    print(f"\n========== {model_name} Evaluation ==========")
    print("Accuracy:", metrics["accuracy"])
    print("Precision:", metrics["precision"])
    print("Recall:", metrics["recall"])
    print("F1 Score:", metrics["f1_score"])
    print("ROC-AUC:", metrics["roc_auc"])
    print("Log Loss:", metrics["log_loss"])
    print("Brier Score:", metrics["brier_score"])
    print("Confusion Matrix:", metrics["confusion_matrix"])

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "w") as file:
            json.dump(metrics, file, indent=4)

        print(f"\nMetrics saved to {save_path}")

    return metrics