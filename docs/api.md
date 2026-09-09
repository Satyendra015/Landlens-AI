# LandLens AI — API Reference (SIH26018)

Interactive OpenAPI Swagger documentation is available at `http://localhost:8000/docs` and ReDoc at `http://localhost:8000/redoc`.

---

## Authentication (`/api/auth`)
- `POST /api/auth/login`: Form-encoded login returning JWT Bearer token.
- `POST /api/auth/json-login`: JSON login endpoint (`{ "email": "...", "password": "..." }`).
- `POST /api/auth/register`: User registration (`name`, `email`, `password`, `role`).
- `GET /api/auth/me`: Retrieves current authenticated user.

---

## Documents (`/api/documents`)
- `POST /api/documents/upload`: Uploads a document (PDF/PNG/JPG). Returns `DocumentOut`.
- `GET /api/documents`: List uploaded documents with pagination and status filter.
- `GET /api/documents/{id}`: Retrieves document metadata.
- `GET /api/documents/{id}/file`: Streams original uploaded file.
- `GET /api/documents/{id}/enhanced-file`: Streams OpenCV preprocessed file.

---

## AI Processing Pipeline (`/api/documents`)
- `POST /api/documents/{id}/process`:
  Executes the end-to-end digitization pipeline:
  1. OpenCV enhancement & quality check.
  2. OCR text extraction.
  3. NLP bilingual field extraction (16 fields).
  4. Multi-factor confidence scoring.
  5. Validation & anomaly detection.
  6. Duplicate detection against database.
  7. Returns `AIProcessingResponse` and creates `LandRecord`.

---

## Land Records (`/api/records`)
- `GET /api/records`: Paginated land records with status and village filters.
- `GET /api/records/search?q={query}`: Universal full-text search across Owner, Khasra, Khata, Village, Tehsil, District.
- `GET /api/records/{id}`: Detailed record view with AI results, verifications, and audit history.
- `PUT /api/records/{id}`: Updates field values with audit logging.
- `POST /api/records/{id}/verify`: Approves record with field corrections and officer notes.
- `POST /api/records/{id}/reject`: Rejects record with mandatory reason.
- `GET /api/records/export?format=csv|json`: Exports digitized records.

---

## Dashboard (`/api/dashboard`)
- `GET /api/dashboard/statistics`: Returns live counts (total, processed, pending, verified, rejected, duplicates, errors, low confidence, distribution charts, and recent activity).

---

## Audit Logs (`/api/audit-logs`)
- `GET /api/audit-logs`: Retrieves immutable audit trail events.

---

## Cadastral GIS (`/api/gis`)
- `GET /api/gis/parcels`: Returns GeoJSON parcel polygon boundaries for demo villages linked to Khasra records.
