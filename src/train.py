# Initiating anomaly detection model training - adding this comment to trigger the CI/CD pipeline via GitHub Actions
"""
Anomaly Detection Training Script — MLOps Portfolio Demo
Treats the ML model as a "black box"; focus is on MLflow instrumentation.
"""

import os
import mlflow
import mlflow.sklearn
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score

# Silence GitPython warning when git is not installed in the container
os.environ.setdefault("GIT_PYTHON_REFRESH", "quiet")

# ── MLflow Configuration ───────────────────────────────────────────────────────
# Read from env so Docker's -e MLFLOW_TRACKING_URI=http://mlflow-server:5000
# takes effect. Falls back to localhost:5000 for bare local runs.
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
EXPERIMENT_NAME = "anomaly-detection"

# ── Hyperparameters ────────────────────────────────────────────────────────────
N_ESTIMATORS = 100
MAX_DEPTH = 8
RANDOM_STATE = 42

mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

with mlflow.start_run(run_name="rf-baseline"):
    # 1. Generate synthetic anomaly-detection dataset (no external data needed)
    X, y = make_classification(
        n_samples=5_000, n_features=20, n_informative=10,
        n_redundant=5, weights=[0.97, 0.03],   # ≈3 % anomaly rate
        random_state=RANDOM_STATE,
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    # 2. Train model
    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS, max_depth=MAX_DEPTH, random_state=RANDOM_STATE
    )
    model.fit(X_train, y_train)

    # 3. Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)

    # 4. Log params, metrics, and the model artifact to MLflow
    mlflow.log_params({
        "n_estimators": N_ESTIMATORS,
        "max_depth": MAX_DEPTH,
        "random_state": RANDOM_STATE,
    })
    mlflow.log_metrics({"accuracy": accuracy, "precision": precision})
    # Upload artifacts via the MLflow server's HTTP proxy endpoint
    # (avoids the trainer needing direct filesystem access to /mlflow/artifacts)
    mlflow.sklearn.log_model(
        model,
        artifact_path="model",
        registered_model_name="AnomalyDetector",
    )

    print(f"[MLflow] Run complete — accuracy={accuracy:.4f}, precision={precision:.4f}")
    print(f"[MLflow] Tracking UI → {TRACKING_URI}")
