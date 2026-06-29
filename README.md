# Secure MLOps Pipeline

[![CI/CD](https://github.com/santosisadora/secure-mlops-pipeline/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/santosisadora/secure-mlops-pipeline/actions/workflows/ci-cd.yml)

A **production-grade, security-first MLOps pipeline** demonstrating enterprise best practices for operationalizing machine learning models in regulated environments (e.g. Capital Markets, FinTech).

> The ML model is intentionally simple. The focus is entirely on the **infrastructure, security, and automation** surrounding it.

---

## Architecture

```
GitHub Push → CI/CD Pipeline (GitHub Actions)
                  │
                  ├── Job 1: flake8 linting
                  ├── Job 2: Docker image build
                  └── Job 3: Trivy security scan (CRITICAL/HIGH = fail)

Local Infrastructure (Docker Compose)
                  │
                  ├── MLflow Tracking Server  →  localhost:5000
                  └── PostgreSQL 15           →  metadata backend store
```

## Features

| Feature | Implementation |
|---|---|
| **Experiment Tracking** | MLflow — logs params, metrics, model artifacts |
| **Model Registry** | MLflow Registry backed by PostgreSQL |
| **Secure Containerization** | Non-root user (UID 10001), `python:3.10-slim` base |
| **Artifact Proxy** | `mlflow-artifacts:/` HTTP proxy — no direct FS access needed |
| **Code Quality Gate** | `flake8` linter enforced in CI |
| **Vulnerability Scanning** | Aqua Trivy — blocks CRITICAL/HIGH CVEs before deployment |
| **Audit Trail** | SARIF results uploaded to GitHub Security tab on every run |
| **Secret Management** | `.env` pattern — credentials never committed to source control |

---

## Project Structure

```
secure-mlops-pipeline/
├── .github/workflows/ci-cd.yml    # 3-job DevSecOps pipeline
├── src/
│   ├── train.py                   # ML training with MLflow instrumentation
│   └── requirements.txt           # Pinned Python dependencies
├── infrastructure/
│   ├── docker-compose.yml         # MLflow Server + PostgreSQL
│   └── Dockerfile.mlflow          # MLflow image with psycopg2 driver
├── Dockerfile                     # Secure non-root training container
├── .dockerignore                  # Prevents secrets leaking into image
└── .env.example                   # Credential template
```

---

## Quick Start

### 1. Start the MLflow Registry

```bash
cp .env.example .env
# Edit .env — set a strong POSTGRES_PASSWORD

docker compose --env-file .env -f infrastructure/docker-compose.yml up -d --build
# Open → http://localhost:5000
```

### 2. Build & Run the Training Container

```bash
docker build -t secure-mlops-trainer:local .

docker run --rm \
  --network infrastructure_mlops-net \
  -e MLFLOW_TRACKING_URI=http://mlflow-server:5000 \
  secure-mlops-trainer:local
```

### 3. View Results

Open **[http://localhost:5000](http://localhost:5000)** → Experiments → `anomaly-detection`

---

## CI/CD Pipeline

Triggered on every push to `main`:

```
lint → build → scan
```

- **Lint**: `flake8` enforces PEP8 code quality
- **Build**: Docker image built with layer caching (GitHub Actions Cache)
- **Scan**: Trivy scans for OS + library CVEs. Pipeline **fails** on CRITICAL/HIGH severity. SARIF report always uploaded to GitHub Security tab for auditability.

---

## Security Controls

| Control | Detail |
|---|---|
| Non-root container | `UID/GID 10001` — limits blast radius of container compromise |
| Minimal base image | `python:3.10-slim` — reduced attack surface vs full Python image |
| No hardcoded secrets | All credentials injected via environment variables |
| `.dockerignore` | Blocks `.env`, keys, certs, git history from image layers |
| Dependency pinning | All versions pinned in `requirements.txt` for reproducibility |
| Trivy gate | Automated CVE scan blocks deployment of vulnerable images |

---

## Tech Stack

`Python` · `scikit-learn` · `MLflow` · `PostgreSQL` · `Docker` · `Docker Compose` · `GitHub Actions` · `Aqua Trivy` · `flake8`

---

## License

MIT
