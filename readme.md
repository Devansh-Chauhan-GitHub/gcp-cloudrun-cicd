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
## 📌 Project Architecture

This project demonstrates a production-grade CI/CD pipeline on Google Cloud Platform.

### Flow Overview
1. Developer pushes code to GitHub
2. GitHub Actions builds Docker image using OIDC authentication
3. Image is pushed to Artifact Registry
4. Cloud Run deploys the container
5. External HTTP Load Balancer routes traffic via Serverless NEG

### Architecture Diagram
![Architecture Diagram](architecture.png)
## 🏗️ Architecture Diagram

📌 [View interactive diagram on Eraser](https://app.eraser.io/workspace/D5RdixWmYoXh3rxFUSLr)

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

##

---

# 🧭 PHASE 2 (GUI) – Artifact Registry + GitHub → GCP Authentication

## 🧱 Visual Flow (Keep This in Mind)

```
GitHub Actions
   ↓ (OIDC)
Workload Identity Provider (GCP IAM)
   ↓
Service Account
   ↓
Artifact Registry
```

---

## 1️⃣ Create Artifact Registry (GCP Console)

### 🔎 Navigation

```
GCP Console → Artifact Registry → Repositories → Create Repository
```

### 📝 Repository Configuration

Fill the form with the following values:

* **Name:** `cloudrun-repo`
* **Format:** Docker
* **Mode:** Standard
* **Region:** `asia-south1`
* **Encryption:** Google-managed key

Click **Create**.

✅ You now have a **private Docker Artifact Registry**.

---

### 🔍 IMPORTANT – Copy Repository Path

After creation:

1. Click on the repository
2. Copy the **Repository path**

It will look like:

```
asia-south1-docker.pkg.dev/PROJECT_ID/cloudrun-repo
```

📌 This value will be used inside **GitHub Actions** to push Docker images.

---

## 2️⃣ Create Service Account (GCP Console)

### 🔎 Navigation

```
IAM & Admin → Service Accounts → Create Service Account
```

---

### Step 1: Service Account Details

* **Name:** `github-actions-sa`
* **Description:** GitHub Actions CI/CD

Click **Create and Continue**.

---

### Step 2: Grant Required Roles

Add the following roles **one by one**:

* **Artifact Registry Writer**
* **Cloud Run Admin**
* **Service Account User**

Click **Done**.

---

## 🔐 What is **Workload Identity**?

**Workload Identity** is a **secure way for applications (workloads) to authenticate to Google Cloud without using long-lived service account keys**.

## 3️⃣ Create Workload Identity Pool (Console)

### Navigation

**IAM & Admin → Workload Identity Federation → Create Pool**

### Pool Details

* **Name**: `github-pool`
* **Description**: GitHub Actions Pool
* **Location**: Global

Click **Continue**

## 4️⃣ Create Workload Identity Provider (GitHub)

### Provider Settings

* **Provider type**: OpenID Connect (OIDC)
* **Provider name**: `github-provider`
* **Issuer URL**:

```
https://token.actions.githubusercontent.com

```

Click **Continue**

---

### Attribute Mapping (VERY IMPORTANT)

In **Attribute Mapping** section:

| Google attributeAssertion |                        |
| ------------------------- | ---------------------- |
| `google.subject`          | `assertion.sub`        |
| `attribute.repository`    | `assertion.repository` |

Click **Save**

✅ GCP now trusts GitHub tokens.

---

## 5️⃣ Link GitHub Repo to Service Account (Console)

This is the **most critical security step**.

### Navigation

**IAM & Admin → Service Accounts → github-actions-sa → Permissions → Grant Access**

### New Principal

Paste this (replace values):

principalSet://iam.googleapis.com/projects/367605285780/locations/global/workloadIdentityPools/github-pool/attribute.repository/Devansh-Chauhan-GitHub/gcp-cloudrun-cicd

# PHASE 3 – GitHub Actions (Build → Push → Deploy)

## 🎯 Goal of this phase

When you do **git push**:

1. Docker image is built
2. Image is pushed to **Artifact Registry**
3. App is deployed to **Cloud Run**

---

## 🧠 Mental flow (keep this clear)

```
GitHub Repo
   ↓ push
GitHub Actions
   ↓ (OIDC auth)
GCP IAM (Service Account)
   ↓
Artifact Registry (Docker image)
   ↓
Cloud Run (new revision)

```

Services involved:

* GitHub Actions
* Artifact Registry
* Cloud Run

---

## 1️⃣ Create workflow directory (in repo)

Inside your repo:

```
.github/
 └── workflows/
     └── deploy.yml

```

👉 This file name can be anything, `deploy.yml` is standard.

---

## 2️⃣ `deploy.yml` (FULL but CLEAN)

Paste this **as-is**, then we’ll adjust values.

```
name: Build & Deploy to Cloud Run

on:
  push:
    branches:
      - main

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Authenticate to GCP
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: projects/367605285780/locations/global/workloadIdentityPools/github-pool/providers/github-provider
        service_account: github-actions-sa@devansh-483504.iam.gserviceaccount.com

    - name: Set up gcloud
      uses: google-github-actions/setup-gcloud@v2

    - name: Configure Docker for Artifact Registry
      run: |
        gcloud auth configure-docker asia-south1-docker.pkg.dev

    - name: Build Docker image
      run: |
        docker build -t asia-south1-docker.pkg.dev/devansh-483504/cloudrun-repo/cloudrun-app:latest .

    - name: Push Docker image
      run: |
        docker push asia-south1-docker.pkg.dev/devansh-483504/cloudrun-repo/cloudrun-app:latest

    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy cloudrun-app \
          --image asia-south1-docker.pkg.dev/devansh-483504/cloudrun-repo/cloudrun-app:latest \
          --region asia-south1 \
          --platform managed \
          --allow-unauthenticated \
          --port 80

```

---

## 3️⃣ Let’s **understand**, not memorize

### 🔹 `permissions`

```
id-token: write

```

➡️ Allows GitHub to generate an **OIDC token**
➡️ Without this → authentication fails

---

### 🔹 Auth step (MOST IMPORTANT)

```
google-github-actions/auth@v2

```

This:

* Uses **OIDC**
* Impersonates your **service account**
* No secrets
* No keys

This is **production-grade GCP CI/CD**.

---

### 🔹 Docker auth

```
gcloud auth configure-docker asia-south1-docker.pkg.dev

```

➡️ Allows Docker to push to Artifact Registry

---

### 🔹 Cloud Run deploy

```
gcloud run deploy

```

Creates:

* A **Cloud Run service**
* New **revision** on every push
* Public endpoint

---

## 4️⃣ Push and WATCH (important)

Commit and push:

```
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Actions CI/CD for Cloud Run"
git push

```

Then:

* Go to **GitHub → Actions**
* Open the workflow
* Watch each step turn ✅ green

---

## ✅ CHECKPOINT

When this finishes successfully:
✔ Docker image exists in **Artifact Registry**
✔ Cloud Run service is created
✔ App is LIVE

You’ll see a URL like:

[https://cloudrun-app-xxxxx-uc.a.run.app](https://cloudrun-app-xxxxx-uc.a.run.app)

---
# 🚀 PHASE 4 – External HTTP Load Balancer in front of Cloud Run

## 🎯 What We Are Doing (Very Clear Goal)

Right now:

* Cloud Run already provides a public HTTPS URL

BUT in real-world architectures:

* We place a **Global HTTP(S) Load Balancer**
* We expose traffic on **port 80 (HTTP)**
* We get **Google Front End (GFE)** benefits:

  * DDoS protection
  * Global anycast IP
  * CDN-ready architecture

---

## 🧠 Architecture (FINAL)

```
Users (HTTP :80)
   ↓
External HTTP Load Balancer (Global IP)
   ↓
Serverless NEG
   ↓
Cloud Run Service
```

### Services Involved

* Cloud Run
* Google Cloud Load Balancing
* Serverless Network Endpoint Group (NEG)

---

## ⚠️ Important Concept (INTERVIEW GOLD)

> **Cloud Run cannot be attached directly to a Load Balancer**

Instead, GCP uses:

```
Load Balancer → Serverless NEG → Cloud Run
```

📌 Remember this line — interviewers love it.

---

## 🧪 STEP 1 – Make Cloud Run Ingress Compatible

### Navigation

```
Cloud Run → cloudrun-app → Edit & Deploy New Revision
```

### Set Ingress

* **Ingress:** ✅ Allow all traffic

Click **Save & Deploy**.

📌 **Why?**
Load Balancer traffic must be allowed to reach Cloud Run.

---

## 🧪 STEP 2 – Create Load Balancer (GUI)

### Navigation

```
Network Services → Load balancing → Create Load Balancer
```

### Choose Load Balancer Type

* **Application Load Balancer (HTTP/S)**
* **From Internet to my VMs or serverless services**

Click **Continue**.

---

## 🧪 STEP 3 – Backend Configuration (MOST IMPORTANT)

### Backend Type

* Select **Serverless network endpoint group**
* Click **Create a serverless NEG**

### Serverless NEG Details

* **Name:** `cloudrun-neg`
* **Region:** `asia-south1`
* **Serverless service:** Cloud Run
* **Service:** `cloudrun-app`

Click **Create**.

✅ Backend successfully connected to Cloud Run.

---

## 🧪 STEP 4 – Frontend Configuration (Port 80)

### Frontend Settings

* **Protocol:** HTTP
* **IP version:** IPv4
* **Port:** 80
* **IP address:** Create new (Global)

📌 Google automatically creates:

* URL map
* Target HTTP proxy
* Forwarding rule

---

## 🧪 STEP 5 – Review & Create

* Review all settings carefully
* Click **Create**

⏳ Wait **2–5 minutes** for provisioning.

---

## ✅ What You Get After Creation

* 🌍 **Global static IP address**
* 🌐 **Public HTTP endpoint on port 80**
* 🚀 Traffic routed directly to Cloud Run

### Example

```
http://34.xxx.xxx.xxx
```

---

## 🧪 STEP 6 – Test

Open in browser:

```
http://<LOAD_BALANCER_IP>
```

You should see:

```
Hello from GCP Cloud Run 🚀
```

---

🎉 **DONE** – Cloud Run is now fronted by a Global External HTTP Load Balancer with Serverless NEG.

