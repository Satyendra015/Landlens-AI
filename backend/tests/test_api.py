import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure root in path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.main import app
from backend.app.database.init_db import init_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()


def test_auth_login():
    """Tests authentication endpoint with default seeded credentials."""
    response = client.post(
        "/api/auth/json-login",
        json={"email": "officer@landlens.gov.in", "password": "officer123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "officer"


def test_auth_invalid_login():
    """Tests rejection of incorrect credentials."""
    response = client.post(
        "/api/auth/json-login",
        json={"email": "officer@landlens.gov.in", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_dashboard_statistics():
    """Tests retrieval of real-time database statistics."""
    # Login first
    login_res = client.post(
        "/api/auth/json-login",
        json={"email": "officer@landlens.gov.in", "password": "officer123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/dashboard/statistics", headers=headers)
    assert response.status_code == 200
    stats = response.json()
    assert "total_documents" in stats
    assert "verified_records" in stats
    assert "status_distribution" in stats
    assert stats["verified_records"] >= 3  # From seeded baseline records


def test_records_search():
    """Tests search API by Khasra number and village."""
    login_res = client.post(
        "/api/auth/json-login",
        json={"email": "officer@landlens.gov.in", "password": "officer123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Search for Rau village
    response = client.get("/api/records/search?q=Rau", headers=headers)
    assert response.status_code == 200
    records = response.json()
    assert len(records) > 0
    assert any("245/2" in r["khasra_number"] for r in records)


def test_records_export_csv():
    """Tests CSV export of land records."""
    login_res = client.post(
        "/api/auth/json-login",
        json={"email": "officer@landlens.gov.in", "password": "officer123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/records/export?format=csv", headers=headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Ram Kumar" in response.text


def test_document_upload_and_ai_process():
    """Tests uploading a synthetic sample document and executing the AI pipeline."""
    login_res = client.post(
        "/api/auth/json-login",
        json={"email": "officer@landlens.gov.in", "password": "officer123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sample_doc_path = os.path.join(root_dir, "data", "sample_documents", "sample_1_clean_rau.png")
    assert os.path.exists(sample_doc_path), f"Sample document not found at {sample_doc_path}"

    # Upload document
    with open(sample_doc_path, "rb") as f:
        upload_res = client.post(
            "/api/documents/upload",
            files={"file": ("sample_1_clean_rau.png", f, "image/png")},
            headers=headers,
        )
    assert upload_res.status_code == 200
    doc_data = upload_res.json()
    doc_id = doc_data["id"]
    assert doc_data["processing_status"] == "uploaded"

    # Process document through AI pipeline
    process_res = client.post(f"/api/documents/{doc_id}/process", headers=headers)
    assert process_res.status_code == 200
    ai_data = process_res.json()
    assert "fields" in ai_data
    assert "overall_confidence" in ai_data
    assert "validation_flags" in ai_data
    assert "duplicate_detection" in ai_data
    assert ai_data["record_id"] is not None

    record_id = ai_data["record_id"]

    # Verify / Approve Record
    verify_res = client.post(
        f"/api/records/{record_id}/verify",
        json={
            "status": "verified",
            "corrections": [],
            "officer_notes": "Automated test verification approved",
        },
        headers=headers,
    )
    assert verify_res.status_code == 200
    verified_data = verify_res.json()
    assert verified_data["verification_status"] == "verified"


def test_ai_adaptation_status_api():
    """Tests retrieval of active learning metrics and experience replay buffer health."""
    login_res = client.post(
        "/api/auth/json-login",
        json={"email": "officer@landlens.gov.in", "password": "officer123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/documents/adaptation-status", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "active"
    assert "total_buffer_size" in data
    assert "metrics" in data


def test_ai_adapt_sample_9_endpoint():
    """Tests the dedicated online adaptation endpoint on sample_9_estamp_ghaziabad."""
    login_res = client.post(
        "/api/auth/json-login",
        json={"email": "officer@landlens.gov.in", "password": "officer123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/documents/adapt-sample-9", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["latency_ms"] < 5000
    assert data["adaptation_accuracy"] >= 90.0


def test_ai_adapt_custom_document_endpoint():
    """Tests real-time online adaptation on arbitrary user-provided land record text."""
    login_res = client.post(
        "/api/auth/json-login",
        json={"email": "officer@landlens.gov.in", "password": "officer123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "text": "GOVERNMENT OF UTTAR PRADESH\nOwner Name : Rajesh Kumar\nFather's Name : Mahesh Kumar\nKhasra Number : 555/1\nVillage : Malihabad\nTehsil : Malihabad\nDistrict : Lucknow\nDate : 10/10/2023",
        "entities": {
            "owner_name": "Rajesh Kumar",
            "father_name": "Mahesh Kumar",
            "khasra_number": "555/1",
            "village": "Malihabad",
            "tehsil": "Malihabad",
            "district": "Lucknow",
            "date": "10/10/2023"
        },
        "doc_type": "user_uploaded_record",
        "doc_name": "custom_realtime_test.png"
    }

    res = client.post("/api/documents/adapt", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["latency_ms"] < 5000
    assert data["adaptation_accuracy"] >= 85.0


def test_process_document_non_land_invoice_rejection():
    """Verifies backend API correctly rejects a commercial tax invoice with is_land_record=False and validation warnings."""
    login_res = client.post(
        "/api/auth/json-login",
        json={"email": "officer@landlens.gov.in", "password": "officer123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sample_invoice_path = os.path.join(root_dir, "data", "sample_documents", "sample_10_non_land_invoice.png")
    # Ensure file exists or render it
    if not os.path.exists(sample_invoice_path):
        from backend.scripts.generate_samples import _render_invoice_image
        _render_invoice_image(sample_invoice_path)

    with open(sample_invoice_path, "rb") as f:
        upload_res = client.post(
            "/api/documents/upload",
            files={"file": ("sample_10_non_land_invoice.png", f, "image/png")},
            headers=headers,
        )
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["id"]

    # Process through AI pipeline
    process_res = client.post(f"/api/documents/{doc_id}/process", headers=headers)
    assert process_res.status_code == 200
    data = process_res.json()

    # Verify discriminator flagged non-land record
    assert data["is_land_record"] is False
    assert data["document_type"] == "invoice_or_billing"
    assert data["warning_message"] is not None
    assert len(data["classification_reasons"]) > 0
    assert data["status"] == "validation_error"

    # Verify validation flag is present
    val_types = [v["type"] for v in data["validation_flags"]]
    assert "invalid_document_type" in val_types


def test_process_document_handwritten_khasra_record():
    """Verifies backend API successfully digitizes handwritten Devanagari land records and normalizes numerals."""
    login_res = client.post(
        "/api/auth/json-login",
        json={"email": "officer@landlens.gov.in", "password": "officer123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sample_hw_path = os.path.join(root_dir, "data", "sample_documents", "sample_11_handwritten_khasra.png")
    if not os.path.exists(sample_hw_path):
        from backend.scripts.generate_samples import _render_handwritten_khasra_image
        _render_handwritten_khasra_image(sample_hw_path)

    with open(sample_hw_path, "rb") as f:
        upload_res = client.post(
            "/api/documents/upload",
            files={"file": ("sample_11_handwritten_khasra.png", f, "image/png")},
            headers=headers,
        )
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["id"]

    process_res = client.post(f"/api/documents/{doc_id}/process", headers=headers)
    assert process_res.status_code == 200
    data = process_res.json()

    assert data["is_land_record"] is True
    assert data["classification_confidence"] >= 0.90
    assert data["fields"]["khasra_number"]["value"] == "245/2"
    assert data["fields"]["khata_number"]["value"] == "112"
    assert "1.25" in data["fields"]["land_area"]["value"]


def test_process_document_generic_non_land_rejection():
    """Verifies that an unclassified arbitrary image without land revenue markings is rejected with validation warnings."""
    login_res = client.post(
        "/api/auth/json-login",
        json={"email": "officer@landlens.gov.in", "password": "officer123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload a synthetic unclassified image
    import io
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (600, 800), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "Weekly Team Meeting Agenda", fill=(0, 0, 0))
    draw.text((50, 100), "Discussion on Cloud Architecture Sprint 12/4", fill=(50, 50, 50))
    draw.text((50, 150), "Notes: Reviewed performance benchmarks.", fill=(50, 50, 50))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    upload_res = client.post(
        "/api/documents/upload",
        files={"file": ("meeting_notes.png", buf, "image/png")},
        headers=headers,
    )
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["id"]

    process_res = client.post(f"/api/documents/{doc_id}/process", headers=headers)
    assert process_res.status_code == 200
    data = process_res.json()

    assert data["is_land_record"] is False
    assert data["status"] == "validation_error"
    assert data["warning_message"] is not None
    val_types = [v["type"] for v in data["validation_flags"]]
    assert "invalid_document_type" in val_types



