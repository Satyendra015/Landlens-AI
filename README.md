# LANDLENS AI

### Intelligent Land Record Digitization & Validation System
> **Smart India Hackathon (SIH26018)**  
> *“From Legacy Land Records to Verified Digital Intelligence.”*

---

## 1. Executive Summary & Problem Statement

Land records across India exist in diverse legacy formats:
- Aging handwritten registers and cadastral field books
- Faded, yellowed, and low-contrast scanned papers
- Multilingual and mixed Hindi (Devanagari) & English documents
- Inconsistent regional formats (Jamabandi, Record of Rights (RoR), Khasra, Khatauni, Nakal, and Mutation registers)

Manual digitization by revenue officials is slow, expensive, prone to manual entry mistakes, and vulnerable to undetectable duplicates or boundary overlap errors.

**LandLens AI** delivers an intelligent, end-to-end digitization and validation platform. It combines Computer Vision image enhancement, multilingual OCR, bilingual NLP field extraction, multi-factor confidence scoring, rule-based validation, fuzzy duplicate detection, and a 3-column Human-in-the-Loop verification studio.

> **Guiding Principle**: *"Let AI perform repetitive work, let validation identify possible problems, and let human officers make the final decision whenever accuracy is uncertain."*

---

## 2. Core Features

1. **Document Ingestion Hub**:
   - Supports PDF, JPG, JPEG, and PNG formats with drag-and-drop file validation and file size protection.
2. **OpenCV Image Preprocessing Pipeline**:
   - Automated quality analysis (Laplacian blur score & contrast evaluation).
   - Bilateral filtering to remove scanner noise without degrading character edges.
   - CLAHE (Contrast Limited Adaptive Histogram Equalization) to recover faded ink.
   - Deskewing and rotation correction using minimum bounding box of text contours.
   - Adaptive Gaussian thresholding for crisp binarization.
   - Interactive Before/After split inspection view in UI.
3. **Modular Multilingual OCR Engine**:
   - Supports English, Hindi (Devanagari), and mixed text.
   - Pluggable provider architecture: EasyOCR, Tesseract, PDF text extractor, and intelligent image reader fallback.
4. **Intelligent Bilingual NLP Field Extraction**:
   - Accurately parses 16 core Indian land attributes:
     - Owner Name (`मालिक का नाम`)
     - Father's/Husband's Name (`पिता का नाम`)
     - Khasra Number (`खसरा नं.`)
     - Khata Number (`खाता नं.`)
     - Survey Number (`सर्वे नं.`)
     - Plot Number (`प्लॉट नं.`)
     - Village (`ग्राम`)
     - Tehsil (`तहसील`)
     - District (`जिला`)
     - State (`राज्य`)
     - Land Area (`रकबा / क्षेत्रफल`)
     - Land Type (`भूमि प्रकार`)
     - Registration Number (`पंजीकरण क्रमांक`)
     - Mutation Number (`नामांतरण क्रमांक`)
     - Document Number (`दस्तावेज संख्या`)
     - Date of Issue (`दिनांक`)
5. **Multi-Factor Extraction Confidence Scoring**:
   - Weighted composite formula: $0.45 \times \text{OCR} + 0.35 \times \text{Pattern} + 0.20 \times \text{Proximity}$.
   - Categorized as **HIGH** ($\ge 90\%$), **MEDIUM** ($70-89\%$), or **LOW** ($< 70\%$).
6. **Validation & Anomaly Engine**:
   - Missing required field detection.
   - Syntax and format validation on Khasra numbers and dates.
   - Range anomaly detection (flags parcels $> 50.0$ Hectares as *"Possible anomaly detected — Unusual Land Area — Please Verify"*).
   - Cross-field consistency (Tehsil vs District lookup).
7. **Fuzzy Duplicate Detection Engine**:
   - Scans database records using normalized composite keys (`khasra + village`) and token-sort Levenshtein distance on owner names (`rapidfuzz`).
   - Generates similarity percentages and comparison links without auto-deleting records.
8. **Human-in-the-Loop (HITL) Verification Studio**:
   - **Column 1**: Document viewer with zoom and Before/After OpenCV toggle.
   - **Column 2**: Bilingual editable fields with inline confidence tags.
   - **Column 3**: AI validation alerts, anomaly warnings, and duplicate match comparisons.
   - **Actions**: Approve record, save individual field corrections, or reject with mandatory reason.
9. **Interactive Cadastral GIS Map Viewer**:
   - Displays geospatial cadastral parcel boundaries for demo villages linked directly to Khasra records.
10. **Central Repository & Search**:
    - Universal search across Owner, Khasra, Khata, Village, Tehsil, and District.
    - Status filtering and one-click CSV/JSON export.
11. **Executive Operational Dashboard**:
    - Real-time KPI metrics, verification status distribution donut chart, confidence histogram, and live activity stream.
12. **Tamper-Evident Audit Trail**:
    - Immutable chronological log capturing every user action, AI processing event, field correction, and approval.

---

## 3. Technology Stack

- **Backend**: Python 3.13 / FastAPI, Uvicorn, Pydantic v2
- **Database**: SQLite (Zero-config out of the box) / PostgreSQL support via SQLAlchemy 2.0
- **Computer Vision**: OpenCV (`cv2`), NumPy, Pillow
- **OCR Engine**: Modular (EasyOCR, Tesseract, pypdf, Adaptive Contour Scanner)
- **NLP & Heuristics**: Regular Expressions, Context Proximity Parsing, RapidFuzz
- **Authentication**: JWT Bearer Tokens, Native Bcrypt, Role-Based Access Control (RBAC)
- **Frontend**: Responsive Single-Page Application, Tailwind CSS, Lucide Icons, Chart.js, Leaflet.js
- **Testing**: Pytest, HTTPX TestClient
- **Containerization**: Docker, Docker Compose

---

## 4. Project Directory Structure

```
landlens-ai/
│
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── cv_pipeline.py          # OpenCV image enhancement & deskewing
│   │   │   ├── ocr_engine.py           # Modular pluggable OCR engine (Hindi + Eng)
│   │   │   ├── field_extractor.py      # Bilingual NLP 16-field parser
│   │   │   ├── confidence_scorer.py    # Multi-factor confidence scoring
│   │   │   └── duplicate_detector.py   # RapidFuzz duplicate detection
│   │   ├── api/
│   │   │   ├── auth.py                 # JWT login & RBAC
│   │   │   ├── documents.py            # File upload & file streaming
│   │   │   ├── ai_process.py           # End-to-end AI pipeline trigger
│   │   │   ├── records.py              # CRUD, search, verification, export
│   │   │   ├── dashboard.py            # Live statistics & chart metrics
│   │   │   ├── audit.py                # Audit trail events
│   │   │   └── gis.py                  # GeoJSON cadastral parcel boundaries
│   │   ├── database/
│   │   │   ├── session.py              # Engine & session maker
│   │   │   └── init_db.py              # Database seeder (default users & records)
│   │   ├── models/
│   │   │   └── models.py               # SQLAlchemy ORM schemas
│   │   ├── schemas/
│   │   │   └── schemas.py              # Pydantic v2 validation models
│   │   ├── static/
│   │   │   ├── index.html              # Responsive single-page UI
│   │   │   └── app.js                  # Frontend client state & interactivity
│   │   ├── validators/
│   │   │   └── validation_engine.py    # Rule engine (Required, Format, Range, Anomaly)
│   │   └── main.py                     # FastAPI application entrypoint
│   ├── scripts/
│   │   ├── generate_samples.py         # 7 synthetic land record generator
│   │   └── evaluate_pipeline.py        # Benchmark accuracy & latency evaluation
│   ├── tests/
│   │   ├── test_api.py                 # API integration tests
│   │   └── test_pipeline.py            # AI & CV unit tests
│   ├── requirements.txt
│   └── run.py                          # Server launcher
│
├── data/
│   ├── sample_documents/               # Synthetic PNG land records
│   └── sample_records/                 # Ground truth metadata JSONs
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── setup.md
│
├── frontend/                           # React + Vite source tree
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 5. Quick Start Instructions

### Prerequisites
- Python 3.10+ installed.

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Initialize Database & Generate Samples
```bash
python backend/app/database/init_db.py
python backend/scripts/generate_samples.py
```

### 3. Launch Server
```bash
python backend/run.py
```

Open your browser at:
👉 **`http://localhost:8000`**

---

## 6. Default User Accounts

| Role | Email | Password |
| :--- | :--- | :--- |
| **Government Officer (Tehsildar)** | `officer@landlens.gov.in` | `officer123` |
| **Super Administrator** | `admin@landlens.gov.in` | `admin123` |
| **Reviewer (Patwari)** | `reviewer@landlens.gov.in` | `reviewer123` |

*(Quick-login buttons are also available directly on the login page.)*

---

## 7. Step-by-Step Hackathon Demonstration Script

Follow this 19-step demonstration flow during your SIH presentation:

1. **Login**: Click **"Officer (Tehsildar)"** on the login screen to sign in as Rajesh Sharma.
2. **Dashboard Overview**: Show live KPI cards, verification status chart, and confidence histogram.
3. **Open Ingestion Hub**: Click **"Upload & Process"** in the top navigation bar.
4. **Select Sample Record**: In the quick scenario bar, click **"2. Faded Record"** (`sample_4_faded_khata_low_confidence.png`) or **"3. Fuzzy Duplicate"** (`sample_5_duplicate_ramkumar.png`).
5. **Inspect Preview**: Observe file metadata, size, and type.
6. **Execute AI Pipeline**: Click **"Execute AI Digitization Pipeline"**.
7. **CV Stepper**: Watch the real-time progress through OpenCV Preprocessing $\rightarrow$ OCR $\rightarrow$ NLP $\rightarrow$ Validation $\rightarrow$ Duplicate Detection.
8. **Inspect Computer Vision Enhancement**: Show the side-by-side **Before & After preview** (CLAHE, Bilateral filtering, and Deskewing).
9. **Enter Verification Studio**: The app automatically transitions to the 3-column Verification Studio.
10. **Left Column**: Show the zoomable historical document; click **"View: Enhanced"** to toggle the cleaned image.
11. **Center Column**: Review the 16 extracted bilingual fields with **HIGH / MEDIUM / LOW** badges.
12. **Right Column**: Point out the AI Intelligence alerts:
    - Low-confidence badge on the faded Khata number.
    - Fuzzy duplicate comparison card linking to matching Khasra 245/2.
13. **Officer Edit**: In the center column, correct the low-confidence field (e.g., change Khata Number to `39`).
14. **Save Corrections**: Click **"Save Corrections"** and observe the instant audit notification.
15. **Approve Record**: Click **"Approve & Digitize"**. The record status updates to **VERIFIED**.
16. **Land Records Repository**: Navigate to **"Land Records"** and search by Khasra number (`245/2`) or Village (`Rau`).
17. **Export**: Click **"Export CSV"** or **"Export JSON"** to demonstrate system interoperability.
18. **Cadastral GIS Map**: Navigate to **"Cadastral GIS"** and click on Khasra `#245/2` parcel to view the popup showing verified ownership.
19. **Audit Ledger**: Open **"Audit Trail"** to show the immutable log recording your verification action with timestamp and officer ID.

---

## 8. Automated Testing & Benchmark Evaluation

### Run Test Suite (11 Tests)
```bash
pytest backend/tests -v
```

### Run Pipeline Evaluation
```bash
python backend/scripts/evaluate_pipeline.py
```
Outputs field extraction precision, recall, F1-score, duplicate detection sensitivity, and average processing latency.

---

## 9. Important Legal & Operational Disclaimer

LandLens AI is an **AI-assisted digitization and decision-support platform** designed to assist government revenue officers. The system **does not** automatically determine legal ownership or issue final legal decrees. All final administrative determinations remain under the statutory jurisdiction of authorized revenue officers.
