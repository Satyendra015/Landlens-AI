import os
import sys
import pytest

# Ensure root in path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.ai.field_extractor import IntelligentFieldExtractor
from backend.app.ai.confidence_scorer import ConfidenceScorer
from backend.app.validators.validation_engine import LandRecordValidator
from backend.app.ai.duplicate_detector import DuplicateDetector
from backend.app.database.session import SessionLocal, Base, engine
from backend.app.models.models import LandRecord


@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


def test_field_extractor_english_and_hindi():
    """Tests extraction of bilingual Indian land record fields."""
    sample_text = """
    GOVERNMENT OF MADHYA PRADESH
    REVENUE DEPARTMENT
    RECORD OF RIGHTS / अधिकार अभिलेख
    Owner Name / मालिक का नाम : Ram Kumar
    Father's Name / पिता का नाम : Shyam Lal
    Khasra Number / खसरा नं. : 245/2
    Khata Number / खाता नं. : 112
    Village / ग्राम : Rau
    Tehsil / तहसील : Rau
    District / जिला : Indore
    Land Area / रकबा : 1.25 Hectare
    Date / दिनांक : 14/08/2023
    """
    fields = IntelligentFieldExtractor.extract_all_fields(sample_text, base_ocr_conf=0.95)

    assert fields["owner_name"].value == "Ram Kumar"
    assert fields["khasra_number"].value == "245/2"
    assert fields["khata_number"].value == "112"
    assert fields["village"].value == "Rau"
    assert fields["tehsil"].value == "Rau"
    assert fields["district"].value == "Indore"
    assert "1.25 Hectare" in fields["land_area"].value
    assert fields["date"].value == "14/08/2023"


def test_confidence_scorer():
    """Tests multi-factor confidence scoring logic."""
    high_conf = ConfidenceScorer.calculate_field_confidence(
        field_name="khasra_number",
        value="245/2",
        raw_ocr_conf=0.96,
        raw_snippet="Khasra No : 245/2",
    )
    assert high_conf["level"] == "HIGH"
    assert high_conf["score"] >= 0.90

    low_conf = ConfidenceScorer.calculate_field_confidence(
        field_name="owner_name",
        value="",
        raw_ocr_conf=0.0,
        raw_snippet="",
    )
    assert low_conf["level"] == "LOW"
    assert low_conf["score"] == 0.0


def test_validator_required_fields():
    """Tests that missing mandatory fields are flagged with error severity."""
    incomplete_record = {
        "owner_name": "Ram Kumar",
        "khasra_number": "",  # Missing
        "village": "Rau",
        "land_area": "",  # Missing
    }
    issues = LandRecordValidator.validate_record(incomplete_record)
    missing_fields = [i.field for i in issues if i.issue_type == "missing_field"]
    assert "khasra_number" in missing_fields
    assert "land_area" in missing_fields


def test_validator_anomaly_area():
    """Tests detection of unusually large land parcel as possible anomaly."""
    anomaly_record = {
        "owner_name": "Kailash Chand",
        "khasra_number": "409/1",
        "village": "Kanadia",
        "land_area": "150.0 Hectare",  # Exceeds 50 Ha limit
    }
    issues = LandRecordValidator.validate_record(anomaly_record)
    anomaly_issues = [i for i in issues if i.issue_type == "unusual_range"]
    assert len(anomaly_issues) > 0
    assert "Unusual Land Area" in anomaly_issues[0].message


def test_duplicate_detector(test_db):
    """Tests fuzzy duplicate identification for matching Khasra and similar owner."""
    # Ensure baseline record exists
    rec = test_db.query(LandRecord).filter(LandRecord.khasra_number == "245/2").first()
    if not rec:
        rec = LandRecord(
            owner_name="Ram Kumar",
            khasra_number="245/2",
            village="Rau",
            tehsil="Rau",
            district="Indore",
        )
        test_db.add(rec)
        test_db.commit()

    # Query with slightly different spelling "Ramkumar"
    result = DuplicateDetector.check_duplicate(
        {"owner_name": "Ramkumar", "khasra_number": "245/2", "village": "Rau"},
        db=test_db,
    )
    assert result["is_duplicate"] is True
    assert result["similarity_score"] >= 75.0
    assert "Identical Khasra #245/2" in result["reasons"][0]


def test_online_continuous_adaptation_on_sample_9_estamp():
    """
    Tests real-time online model adaptation on Uttar Pradesh e-Stamp Conveyance Deed
    (sample_9_estamp_ghaziabad.jpg) and verifies > 90% confidence across fields.
    """
    from backend.app.ai.online_learner import OnlineContinuousLearner
    from backend.app.ai.ocr_engine import ModularOCREngine

    txt_path = os.path.join(root_dir, "data", "sample_documents", "sample_9_estamp_ghaziabad_ground_truth.txt")
    json_path = os.path.join(root_dir, "data", "sample_records", "sample_9_estamp_ghaziabad.json")
    img_path = os.path.join(root_dir, "data", "sample_documents", "sample_9_estamp_ghaziabad.jpg")

    assert os.path.exists(txt_path), f"Ground truth missing: {txt_path}"
    assert os.path.exists(json_path), f"Sample record missing: {json_path}"

    import json
    with open(txt_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    with open(json_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    learner = OnlineContinuousLearner()

    # Adapt online
    res = learner.adapt_on_document(
        text=raw_text,
        entities=meta.get("fields", {}),
        doc_type="estamp_conveyance_deed",
        doc_name="sample_9_estamp_ghaziabad.jpg"
    )

    assert res["success"] is True
    assert res["latency_ms"] < 5000  # Highly efficient adaptation
    assert res["adaptation_accuracy"] >= 90.0

    # Run extraction and confidence scoring on adapted document
    ocr_engine = ModularOCREngine()
    ocr_res = ocr_engine.process_document(img_path, document_name="sample_9_estamp_ghaziabad.jpg")
    extracted = IntelligentFieldExtractor.extract_all_fields(ocr_res.raw_text, base_ocr_conf=ocr_res.average_confidence)

    # Verify key conveyance deed attributes
    expected_fields = meta["fields"]
    assert extracted["owner_name"].value.lower() == expected_fields["owner_name"].lower()
    assert extracted["khasra_number"].value.lower() == expected_fields["khasra_number"].lower()
    assert extracted["khata_number"].value.lower() == expected_fields["khata_number"].lower()
    assert extracted["village"].value.lower() == expected_fields["village"].lower()
    assert extracted["tehsil"].value.lower() == expected_fields["tehsil"].lower()
    assert extracted["district"].value.lower() == expected_fields["district"].lower()
    assert extracted["state"].value.lower() == expected_fields["state"].lower()
    assert extracted["land_type"].value.lower() == expected_fields["land_type"].lower()
    assert extracted["registration_number"].value.lower() == expected_fields["registration_number"].lower()
    assert extracted["mutation_number"].value.lower() == expected_fields["mutation_number"].lower()
    assert extracted["document_number"].value.lower() == expected_fields["document_number"].lower()
    assert extracted["date"].value.lower() == expected_fields["date"].lower()

    # Verify High Confidence (> 90%)
    for f_name in ["owner_name", "khasra_number", "khata_number", "village", "district", "registration_number", "date"]:
        f_obj = extracted[f_name]
        conf_data = ConfidenceScorer.calculate_field_confidence(
            f_name, f_obj.value, f_obj.confidence, raw_snippet=f_obj.raw_ocr, flag=f_obj.flag
        )
        assert conf_data["level"] == "HIGH", f"Field '{f_name}' confidence {conf_data['score']} is not HIGH"
        assert conf_data["score"] >= 0.90, f"Field '{f_name}' score {conf_data['score']} < 0.90"


def test_anti_catastrophic_forgetting():
    """Verifies that adapting on new conveyance deeds does not degrade performance on historical Jamabandi records."""
    from backend.app.ai.ocr_engine import ModularOCREngine
    ocr_engine = ModularOCREngine()

    sample_1_path = os.path.join(root_dir, "data", "sample_documents", "sample_1_clean_rau.png")
    ocr_res = ocr_engine.process_document(sample_1_path, document_name="sample_1_clean_rau.png")
    extracted = IntelligentFieldExtractor.extract_all_fields(ocr_res.raw_text, base_ocr_conf=ocr_res.average_confidence)

    assert extracted["owner_name"].value == "Ram Kumar"
    assert extracted["khasra_number"].value == "245/2"
    assert extracted["village"].value == "Rau"

    conf = ConfidenceScorer.calculate_field_confidence(
        "owner_name", extracted["owner_name"].value, extracted["owner_name"].confidence,
        raw_snippet=extracted["owner_name"].raw_ocr, flag=extracted["owner_name"].flag
    )
    assert conf["level"] == "HIGH"
    assert conf["score"] >= 0.90


def test_date_normalization_and_property_decomposition():
    """Tests date standardization and composite property line decomposition."""
    norm_date = IntelligentFieldExtractor._normalize_date("01-Jun-2021 01:51 PM")
    assert norm_date == "01/06/2021"

    text = "Property Description : FLAT NO 1101 11th FLOOR MILLENIA EMERALD HEIGHTS SEC-7 RAMFRASTHA GREENS VAISHALI EXTN, GZB"
    decomp = IntelligentFieldExtractor._extract_property_description_fields(text)
    assert decomp["khata_number"] == "Flat No 1101"
    assert decomp["plot_number"] == "Flat 1101"
    assert "Sec-7 Ramprastha Greens" in decomp["khasra_number"]
    assert decomp["village"] == "Vaishali Extn"
    assert decomp["tehsil"] == "Ghaziabad"
    assert decomp["district"] == "Ghaziabad"


def test_validator_urban_deed_flat_area_not_anomaly():
    """Verifies that urban flat/floor parcel descriptors are not falsely flagged as anomalous hectares."""
    urban_record = {
        "owner_name": "Pankaj Tyagi and Amrita Tyagi",
        "khasra_number": "Sec-7 Ramprastha Greens",
        "village": "Vaishali Extn",
        "land_area": "Flat No 1101 11th Floor",
        "district": "Ghaziabad",
        "tehsil": "Ghaziabad",
    }
    issues = LandRecordValidator.validate_record(urban_record)
    anomaly_issues = [i for i in issues if i.issue_type == "unusual_range"]
    assert len(anomaly_issues) == 0, f"Unexpected anomaly flags for urban deed: {[i.message for i in anomaly_issues]}"


def test_label_document_tokens_authentic_estamp():
    """Verifies token alignment and BIO tag assignment on authentic e-stamp deed text without synthetic headers."""
    from backend.app.ai.online_learner import label_document_tokens
    authentic_text = (
        "Purchased by : PANKAJ TYAGI AND AMRITA TYAGI\n"
        "First Party : KIRAN VERMA GPA HOLDER OF PINKY SEHDEV\n"
        "Certificate No. : IN-UP76993801475378T\n"
        "Certificate Issued Date : 01-Jun-2021 01:51 PM\n"
        "Account Reference : NEWIMPACC (SV)/ up14000104/ GHAZIABAD/ UP-GZB\n"
    )
    entities = {
        "owner_name": "Pankaj Tyagi and Amrita Tyagi",
        "father_name": "Kiran Verma GPA Holder of Pinky Sehdev",
        "registration_number": "IN-UP76993801475378T",
        "mutation_number": "up14000104",
        "date": "01/06/2021",
    }
    tokens, labels = label_document_tokens(authentic_text, entities)
    assert "B-OWNER" in labels
    assert "I-OWNER" in labels
    assert "B-FATHER" in labels
    assert "B-REG_NO" in labels
    assert "B-MUTATION" in labels
    assert "B-DATE" in labels


def test_document_discriminator_genuine_land_records():
    """Verifies that authentic land records (Jamabandi, e-Stamp, Handwritten) are correctly identified as land records."""
    from backend.app.ai.document_classifier import get_document_classifier
    classifier = get_document_classifier()

    # 1. Jamabandi RoR
    jamabandi_text = (
        "GOVERNMENT OF MADHYA PRADESH - REVENUE DEPARTMENT\n"
        "RECORD OF RIGHTS / अधिकार अभिलेख जमाबंदी\n"
        "Owner Name / मालिक का नाम : Ram Kumar\n"
        "Khasra Number / खसरा नं. : 245/2\n"
        "Village / ग्राम : Rau\n"
        "Tehsil / तहसील : Rau\n"
        "District / जिला : Indore\n"
        "Land Area / रकबा : 1.25 Hectare\n"
    )
    res_jama = classifier.classify_text(jamabandi_text)
    assert res_jama.is_land_record is True
    assert res_jama.confidence >= 0.90
    assert res_jama.document_type == "jamabandi_ror"

    # 2. UP e-Stamp Conveyance Deed
    estamp_text = (
        "INDIA NON JUDICIAL\n"
        "Government of Uttar Pradesh\n"
        "e-Stamp\n"
        "Certificate No. : IN-UP76993801475378T\n"
        "Article 23 Conveyance\n"
        "Purchased by : PANKAJ TYAGI AND AMRITA TYAGI\n"
        "Property Description : FLAT NO 1101 11th FLOOR VAISHALI EXTN GZB\n"
    )
    res_estamp = classifier.classify_text(estamp_text)
    assert res_estamp.is_land_record is True
    assert res_estamp.confidence >= 0.90
    assert res_estamp.document_type == "estamp_conveyance_deed"

    # 3. Handwritten Devanagari Record
    handwritten_text = (
        "मध्य प्रदेश शासन - राजस्व विभाग\n"
        "अधिकार अभिलेख (हस्तलिखित खसरा पंजी)\n"
        "मालिक का नाम : राम कुमार\n"
        "पिता का नाम : श्याम लाल\n"
        "खसरा नं. : २४५/२\n"
        "खाता नं. : ११२\n"
        "ग्राम : राऊ\n"
        "रकबा : १.२५ हेक्टेयर\n"
    )
    res_hw = classifier.classify_text(handwritten_text)
    assert res_hw.is_land_record is True
    assert res_hw.confidence >= 0.90


def test_document_discriminator_rejects_non_land_documents():
    """Verifies that non-land documents (invoices, resumes, generic text) are rejected with clear warnings."""
    from backend.app.ai.document_classifier import get_document_classifier
    classifier = get_document_classifier()

    # 1. Commercial Tax Invoice
    invoice_text = (
        "TAX INVOICE / बिल\n"
        "Invoice No : INV-2024-8891\n"
        "Date : 15/03/2024\n"
        "Bill To : Acme Enterprises Pvt Ltd\n"
        "GSTIN : 07AAAAA0000A1Z5\n"
        "Description : Cloud Hosting Services\n"
        "Quantity : 1\n"
        "Subtotal : Rs. 4,500.00\n"
        "Total Amount Due : Rs. 5,310.00\n"
        "Payment Terms : Net 30 Days\n"
    )
    res_inv = classifier.classify_text(invoice_text)
    assert res_inv.is_land_record is False
    assert res_inv.document_type == "invoice_or_billing"
    assert res_inv.warning_message is not None
    assert "Tax Invoice" in res_inv.warning_message or "commercial" in res_inv.warning_message.lower() or "invoice" in res_inv.warning_message.lower()

    # 2. Resume / Curriculum Vitae
    resume_text = (
        "CURRICULUM VITAE\n"
        "Candidate Name : John Doe\n"
        "Professional Experience : Senior Python Software Developer at Global Tech\n"
        "Education : Bachelor of Technology in Computer Science\n"
        "Technical Skills : Python, FastAPI, Docker, PostgreSQL\n"
    )
    res_cv = classifier.classify_text(resume_text)
    assert res_cv.is_land_record is False
    assert res_cv.warning_message is not None

    # 3. Short / Unrelated text
    empty_res = classifier.classify_text("Hello world testing 123")
    assert empty_res.is_land_record is False


def test_handwritten_devanagari_numeral_normalization():
    """Verifies that Devanagari numerals (०-९) in handwritten land records are normalized to standard Arabic digits (0-9)."""
    hw_text = (
        "GOVERNMENT OF MADHYA PRADESH\n"
        "REVENUE DEPARTMENT / राजस्व विभाग\n"
        "अधिकार अभिलेख (हस्तलिखित खसरा)\n"
        "Owner Name / मालिक का नाम : राम कुमार\n"
        "Khasra Number / खसरा नं. : २४५/२\n"
        "Khata Number / खाता नं. : ११२\n"
        "Survey Number / सर्वे नं. : ८८२\n"
        "Plot Number / प्लॉट नं. : १२\n"
        "Village / ग्राम : राऊ\n"
        "Tehsil / तहसील : राऊ\n"
        "District / जिला : इंदौर\n"
        "Land Area / रकबा : १.२५ हेक्टेयर\n"
        "Date / दिनांक : १४/०८/२०२३\n"
    )
    extracted = IntelligentFieldExtractor.extract_all_fields(hw_text, base_ocr_conf=0.95)

    assert extracted["khasra_number"].value == "245/2"
    assert extracted["khata_number"].value == "112"
    assert extracted["survey_number"].value == "882"
    assert extracted["plot_number"].value == "12"
    assert "1.25" in extracted["land_area"].value
    assert extracted["date"].value == "14/08/2023"


def test_discriminator_online_adaptation():
    """Verifies real-time online continuous learning of the discriminator."""
    from backend.app.ai.document_classifier import get_document_classifier
    classifier = get_document_classifier()

    realtime_record = (
        "STATE OF BIHAR - REVENUE & LAND REFORMS DEPARTMENT\n"
        "KHATIAN REGISTER / अधिकार अभिलेख\n"
        "Raiyat Name / रैयत का नाम : Suresh Prasad\n"
        "Khasra No / खेसरा सं. : 110/3\n"
        "Khata No / खाता सं. : 74\n"
        "Thana No / थाना सं. : 201\n"
        "Anchal / अंचल : Patna Sadar\n"
        "District / जिला : Patna\n"
        "Rakba / रकबा : 2.50 Bigha\n"
    )
    classifier.adapt_realtime(realtime_record, is_land_record=True, doc_type="bihar_khatian")
    res = classifier.classify_text(realtime_record)
    assert res.is_land_record is True
    assert res.confidence >= 0.90


def test_discriminator_rejects_slash_patterns_without_revenue_context():
    """Verifies that arbitrary text with slash patterns (fractions, dates, addresses) without revenue context is rejected."""
    from backend.app.ai.document_classifier import get_document_classifier
    classifier = get_document_classifier()

    # Generic meeting notes with dates and fractions
    notes_text = (
        "Project Sprint Review Meeting Notes\n"
        "Date: 14/08/2023\n"
        "Task completed: 12/4 submodules migrated.\n"
        "Office Location: 245/2 Baker Street, 4th Floor.\n"
        "Attendees: Ram Kumar, Shyam Lal."
    )
    res = classifier.classify_text(notes_text)
    assert res.is_land_record is False
    assert res.document_type == "generic_non_land_document"
    assert res.warning_message is not None


def test_discriminator_rejects_utility_and_banking_documents():
    """Verifies rejection of electricity bills and bank statements with incidental geo-names."""
    from backend.app.ai.document_classifier import get_document_classifier
    classifier = get_document_classifier()

    utility_text = (
        "STATE POWER DISTRIBUTION COMPANY\n"
        "ELECTRICITY BILL / उपभोक्ता बिल\n"
        "Consumer No: 9817263541\n"
        "Meter Number: EM-2023\n"
        "Units Consumed: 340 kWh\n"
        "Total Amount Due: Rs. 2,850.00\n"
        "Due Date: 25/03/2024\n"
        "Subdivision: Indore District"
    )
    res = classifier.classify_text(utility_text)
    assert res.is_land_record is False
    assert res.document_type == "utility_bill"
    assert "Electricity" in res.warning_message or "Utility" in res.warning_message


def test_discriminator_continuous_multi_document_adaptation():
    """Verifies that multiple consecutive real-time adaptations accumulate knowledge without forgetting previous documents."""
    from backend.app.ai.document_classifier import get_document_classifier
    classifier = get_document_classifier()

    doc_1 = (
        "ASSAM REVENUE & DISASTER MANAGEMENT DEPARTMENT\n"
        "CHITHA REGISTER / अधिकार अभिलेख\n"
        "Pattadar Name: Biren Saikia\n"
        "Dag No: 442/1\n"
        "Patta No: 88\n"
        "Mouza: Sonapur\n"
        "District: Kamrup Metropolitan\n"
        "Area: 3.5 Bigha"
    )
    doc_2 = (
        "GOVERNMENT OF PUNJAB - DEPARTMENT OF REVENUE\n"
        "FARAD JAMABANDI / ਫ਼ਰਦ ਜਮ੍ਹਾਂਬੰਦੀ\n"
        "Khewat No: 104\n"
        "Khatoni No: 219\n"
        "Khasra No: 55//12/2\n"
        "Village: Mansa\n"
        "Tehsil: Mansa\n"
        "Area: 4 Kanal 10 Marla"
    )

    classifier.adapt_realtime(doc_1, is_land_record=True, doc_type="assam_chitha")
    classifier.adapt_realtime(doc_2, is_land_record=True, doc_type="punjab_jamabandi")

    # Both documents must be recognized as genuine land records
    res_1 = classifier.classify_text(doc_1)
    res_2 = classifier.classify_text(doc_2)
    assert res_1.is_land_record is True
    assert res_2.is_land_record is True


def test_handwritten_mutation_and_reg_number_devanagari_normalization():
    """Verifies that Devanagari digits in mutation and registration numbers are converted to Arabic digits."""
    hw_text = (
        "मध्य प्रदेश शासन - राजस्व विभाग\n"
        "हस्तलिखित अधिकार अभिलेख\n"
        "मालिक का नाम : राम कुमार\n"
        "खसरा नं. : २४५/२\n"
        "पंजीकरण क्रमांक : ९९०१\n"
        "नामांतरण क्रमांक : ४४१\n"
        "दस्तावेज संख्या : ५५\n"
        "दिनांक : १४/०८/२०२३\n"
    )
    extracted = IntelligentFieldExtractor.extract_all_fields(hw_text, base_ocr_conf=0.95)
    assert extracted["khasra_number"].value == "245/2"
    assert extracted["registration_number"].value == "9901"
    assert extracted["mutation_number"].value == "441"
    assert extracted["document_number"].value == "55"
    assert extracted["date"].value == "14/08/2023"



