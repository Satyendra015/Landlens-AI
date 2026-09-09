# LandLens AI — Setup & Deployment Guide

## Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Optional: Node.js 18+ (if running Vite development server independently)
- Optional: Docker & Docker Compose

---

## 1. Quick Local Setup (Single Command)

### Step 1: Install Python Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 2: Initialize Database & Seed Demo Data
```bash
python backend/app/database/init_db.py
```

### Step 3: Generate Synthetic Land Record Dataset
```bash
python backend/scripts/generate_samples.py
```

### Step 4: Run Application Server
```bash
python backend/run.py
```

Open your browser and navigate to:
**`http://localhost:8000`**

---

## 2. Default Login Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| **Government Officer (Tehsildar)** | `officer@landlens.gov.in` | `officer123` |
| **Super Administrator** | `admin@landlens.gov.in` | `admin123` |
| **Reviewer (Patwari)** | `reviewer@landlens.gov.in` | `reviewer123` |

*(You can also use the 1-click quick login buttons on the login screen!)*

---

## 3. Running Automated Tests & Benchmark

### Run Pytest Test Suite
```bash
pytest backend/tests -v
```

### Run Extraction & Benchmark Evaluation
```bash
python backend/scripts/evaluate_pipeline.py
```

---

## 4. Docker Deployment
```bash
docker-compose up --build
```
The application will be accessible at `http://localhost:8000`.
