# LandLens AI — Technical Architecture (SIH26018)

## 1. System Overview
LandLens AI is an AI-assisted land-record digitization and validation platform built to solve **SIH26018**. It bridges the gap between degraded historical legacy records (faded paper, handwritten registers, complex bilingual layouts) and modern verifiable digital land registries.

## 2. Core Architectural Components

### A. Computer Vision Preprocessing Pipeline (`cv_pipeline.py`)
- **Quality Assessment**: Evaluates Laplacian variance (blur score) and pixel intensity standard deviation (contrast score).
- **Bilateral Filtering**: Eliminates scanner paper speckles and yellowing while retaining sharp character boundaries.
- **CLAHE (Contrast Limited Adaptive Histogram Equalization)**: Rescues low-contrast or faded ink entries.
- **Deskewing**: Calculates the minimum area bounding box of detected text contours and applies an affine rotation transformation to straighten tilted scans.
- **Adaptive Gaussian Thresholding**: Converts multi-shade paper textures into high-contrast monochrome text for OCR parsing.

### B. Modular Pluggable OCR Architecture (`ocr_engine.py`)
- **BaseOCREngine Interface**: Allows dynamic runtime swapping of OCR providers without modifying downstream logic.
- **EasyOCRProvider**: Deep learning-based text detection supporting bilingual English and Devanagari (Hindi) scripts.
- **TesseractProvider**: System-level OCR integration via pytesseract.
- **PDFTextProvider**: Direct stream extractor for digital vector PDFs.
- **IntelligentImageReaderProvider**: Fallback parser ensuring 100% operational resilience.

### C. Bilingual Field Extraction & NLP Engine (`field_extractor.py`)
Extracts the 16 standard Indian land record attributes:
1. `owner_name` (मालिक / खातेदार का नाम)
2. `father_name` (पिता / पति का नाम)
3. `khasra_number` (खसरा नं.)
4. `khata_number` (खाता नं. / खेवट)
5. `survey_number` (सर्वे नं.)
6. `plot_number` (प्लॉट नं.)
7. `village` (ग्राम / मौजा)
8. `tehsil` (तहसील / तालुका)
9. `district` (जिला)
10. `state` (राज्य)
11. `land_area` (रकबा / क्षेत्रफल)
12. `land_type` (भूमि प्रकार)
13. `registration_number` (पंजीकरण क्रमांक)
14. `mutation_number` (दाखिल खारिज / नामांतरण)
15. `document_number` (दस्तावेज संख्या)
16. `date` (दिनांक)

### D. Multi-Factor Confidence Scoring (`confidence_scorer.py`)
$$\text{Composite Score} = 0.45 \times \text{OCR} + 0.35 \times \text{Pattern Match} + 0.20 \times \text{Proximity}$$
- **HIGH**: $\ge 90\%$ (Green)
- **MEDIUM**: $70 - 89\%$ (Amber)
- **LOW**: $< 70\%$ (Red — triggers mandatory human verification)

### E. Validation Engine (`validation_engine.py`)
- **Required Field Validation**: Verifies presence of core attributes.
- **Format Validation**: Ensures syntactic adherence of Khasra numbers and dates.
- **Range & Anomaly Validation**: Flags parcels exceeding 50.0 Hectares as "Possible anomaly detected — Unusual Land Area — Please Verify".
- **Cross-Field Validation**: Validates Tehsil and District geographic alignment.
- **Consistency Validation**: Cross-checks against database records to detect conflicting ownership for the same Khasra/Village.

### F. Duplicate Detection Engine (`duplicate_detector.py`)
- Combines exact normalized composite matching (`khasra + village`) with token-sort Levenshtein similarity on owner names (`rapidfuzz`).
- Generates a match similarity score without auto-deleting records, empowering the officer with side-by-side comparison.

### G. Human-in-the-Loop (HITL) Studio
3-column verification workspace:
- **Left**: Zoomable document image with Before/After OpenCV preview.
- **Center**: Editable bilingual inputs with confidence tags and field-level confirmation.
- **Right**: Rule engine flags, duplicate comparison alerts, and anomaly notices.
- **Governance**: Every edit, approval, and rejection is recorded into the audit trail.
