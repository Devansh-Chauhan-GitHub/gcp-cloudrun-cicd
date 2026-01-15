# 🚀 GCP Cloud Run CI/CD Project (GitHub → Artifact Registry → Cloud Run)

This project demonstrates a complete **CI/CD workflow on Google Cloud Platform (GCP)** where a simple Flask application is:

* Stored in **GitHub**
* Containerized using **Docker**
* Built & pushed to **Artifact Registry**
* Deployed on **Cloud Run**
* Served publicly on **Port 80**

---

## 🧱 Architecture Overview

```
GitHub Repository
      ↓
GitHub Actions (CI)
      ↓
Docker Image
      ↓
Artifact Registry (GCP)
      ↓
Cloud Run
      ↓
Public HTTPS Endpoint (Port 80)
```

---

## ✅ Prerequisites

* Google Cloud account
* GCP Project created
* `gcloud` CLI installed
* GitHub account

---

## 2️⃣ Enable Required GCP APIs

Enable these APIs **once per project**:

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com \
  compute.googleapis.com
```

⚠️ These APIs are mandatory for Cloud Run and Artifact Registry.

---

## 3️⃣ Install & Configure gcloud

### Check gcloud installation

```bash
gcloud version
```

### Authenticate

```bash
gcloud auth login
gcloud auth application-default login
```

### Set GCP project

```bash
gcloud config set project YOUR_PROJECT_ID
```

---

# 🚀 PHASE 1 – GitHub Repository & Application Setup

---

## 1️⃣ Create GitHub Repository

* **Repository name:** `gcp-cloudrun-cicd`
* **Visibility:** Public or Private

---

## 2️⃣ Create Simple Flask Application (Port 80)

### `app.py`

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from GCP Cloud Run 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
```

### `requirements.txt`

```
flask
```

---

## 3️⃣ Dockerfile (VERY IMPORTANT)

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

EXPOSE 80

CMD ["python", "app.py"]
```

### Important Notes

* Cloud Run requires the application to listen on the provided port
* `0.0.0.0` is mandatory for container networking
* Port **80** is explicitly used

---

## 4️⃣ Push Code to GitHub

```bash
git init
git add .
git commit -m "Initial Flask app with Dockerfile"
git branch -M main
git remote add origin https://github.com/<your-username>/gcp-cloudrun-cicd.git
git push -u origin main
```

---

## 📁 Project Structure

```
gcp-cloudrun-cicd/
│
├── app.py
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🔜 Next Steps

* Create Artifact Registry
* Configure IAM & Service Account
* Setup GitHub Actions (CI/CD)
* Push image to Artifact Registry
* Deploy application to Cloud Run
* (Optional) Attach Load Balancer

---

## 🧠 What You’ll Learn

* Cloud Run deployment workflow
* Docker image lifecycle in GCP
* Artifact Registry usage
* GitHub Actions for CI/CD
* IAM basics for Cloud Run

---

🚀 **This project is beginner-friendly and production-oriented, designed to demonstrate real-world GCP CI/CD practic

