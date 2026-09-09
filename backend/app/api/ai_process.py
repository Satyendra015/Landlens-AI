import os
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import (
    Document,
    LandRecord,
    AIResult,
    ProcessingStatus,
    VerificationStatus,
    AuditLog,
    User,
)
from backend.app.schemas.schemas import (
    AIProcessingResponse,
    FieldScore,
    ValidationFlag,
    DuplicateMatch,
    AdaptationRequest,
    AdaptationResponse,
)
from backend.app.services.auth import get_current_user
from backend.app.ai.cv_pipeline import DocumentCVPipeline
from backend.app.ai.ocr_engine import ModularOCREngine
from backend.app.ai.field_extractor import IntelligentFieldExtractor
from backend.app.ai.confidence_scorer import ConfidenceScorer
from backend.app.validators.validation_engine import LandRecordValidator
from backend.app.ai.duplicate_detector import DuplicateDetector
from backend.app.ai.document_classifier import get_document_classifier

router = APIRouter(prefix="/api/documents", tags=["AI Processing Pipeline"])

ocr_engine = ModularOCREngine()


@router.post("/{document_id}/process", response_model=AIProcessingResponse)
def process_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Executes the end-to-end LandLens AI digitization pipeline:
    Upload -> Image Enhancement (OpenCV) -> OCR -> Field Extraction ->
    Confidence Scoring -> Validation -> Duplicate Detection -> Database Storage.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=400, detail="Document file missing from storage.")

    # Update document status to processing
    doc.processing_status = ProcessingStatus.PROCESSING.value
    db.commit()

    try:
        # Step 0: Image & Document File Metadata
        img_width, img_height = 0, 0
        try:
            from PIL import Image
            with Image.open(doc.file_path) as im:
                img_width, img_height = im.size
        except Exception:
            pass

        file_meta = {
            "filename": doc.filename,
            "file_size": doc.file_size,
            "file_type": doc.file_type,
            "width": img_width,
            "height": img_height,
            "dimensions": f"{img_width} x {img_height} px" if img_width and img_height else "Unknown",
        }

        # Step 1: Computer Vision Preprocessing & Enhancement
        enhanced_filename = f"enhanced_{os.path.splitext(os.path.basename(doc.file_path))[0]}.png"
        enhanced_path = os.path.join(os.path.dirname(doc.file_path), "..", "enhanced", enhanced_filename)
        enhanced_path = os.path.abspath(enhanced_path)

        enhanced_path, cv_metrics = DocumentCVPipeline.enhance_document(doc.file_path, enhanced_path)
        doc.preprocessed_path = enhanced_path

        # Step 2: Modular Real OCR on Enhanced Document
        ocr_target = enhanced_path if os.path.exists(enhanced_path) else doc.file_path
        is_live = not doc.filename.startswith("sample_")
        ocr_result = ocr_engine.process_document(
            ocr_target, document_name=doc.filename, is_live_upload=is_live
        )

        # Step 2.5: Intelligent Document Discrimination & Classification (SIH26018)
        classifier = get_document_classifier()
        doc_class_result = classifier.classify_document(
            raw_text=ocr_result.raw_text,
            file_path=ocr_target,
            document_name=doc.filename,
        )

        # Step 3: Intelligent NLP Field Extraction (with Evidence & Zero Hallucination)
        extracted_fields = IntelligentFieldExtractor.extract_all_fields(
            raw_text=ocr_result.raw_text,
            base_ocr_conf=ocr_result.average_confidence,
            image_path=ocr_target,
        )

        # Build clean dictionary of extracted values
        extracted_dict = {f: extracted_fields[f].value for f in extracted_fields}

        # Step 4: Multi-Factor Confidence Scoring for each field
        field_scores = {}
        confidences = []
        has_low_confidence = False

        for f_name, f_obj in extracted_fields.items():
            conf_details = ConfidenceScorer.calculate_field_confidence(
                field_name=f_name,
                value=f_obj.value,
                raw_ocr_conf=f_obj.confidence,
                raw_snippet=f_obj.raw_ocr,
                flag=f_obj.flag or "",
            )
            score = conf_details["score"]
            level = conf_details["level"]
            if level == "LOW" and f_obj.value:
                has_low_confidence = True

            if f_obj.value:
                confidences.append(score)

            field_scores[f_name] = FieldScore(
                value=f_obj.value,
                confidence=score,
                level=level,
                status="valid" if f_obj.value else "missing",
                flag=conf_details["label"],
                raw_ocr=f_obj.raw_ocr,
                source_text=getattr(f_obj, "source_text", f_obj.raw_ocr),
            )

        overall_conf = (
            round(sum(confidences) / max(len(confidences), 1), 3) if confidences else 0.0
        )

        # Step 5: Comprehensive Validation Engine
        validation_issues = LandRecordValidator.validate_record(extracted_dict, db=db)

        # Check document classification validation
        doc_issue = LandRecordValidator.validate_document_classification(
            doc_class_result.is_land_record,
            doc_class_result.document_type,
            doc_class_result.warning_message,
        )
        if doc_issue:
            validation_issues.insert(0, doc_issue)

        val_flags = [
            ValidationFlag(
                field=iss.field,
                type=iss.issue_type,
                message=iss.message,
                severity=iss.severity,
            )
            for iss in validation_issues
        ]

        # Step 6: Duplicate Detection Engine
        duplicate_data = DuplicateDetector.check_duplicate(extracted_dict, db=db)
        duplicate_match = DuplicateMatch(
            is_duplicate=duplicate_data.get("is_duplicate", False),
            similarity_score=duplicate_data.get("similarity_score", 0.0),
            matched_record_id=duplicate_data.get("matched_record_id"),
            matched_khasra=duplicate_data.get("matched_khasra"),
            matched_owner=duplicate_data.get("matched_owner"),
            matched_village=duplicate_data.get("matched_village"),
            reasons=duplicate_data.get("reasons", []),
        )

        # Determine Verification Status
        if not doc_class_result.is_land_record:
            final_status = VerificationStatus.VALIDATION_ERROR.value
        elif duplicate_match.is_duplicate:
            final_status = VerificationStatus.POSSIBLE_DUPLICATE.value
        elif any(v.severity == "error" for v in val_flags):
            final_status = VerificationStatus.VALIDATION_ERROR.value
        elif has_low_confidence or any(v.severity == "warning" for v in val_flags):
            final_status = VerificationStatus.REQUIRES_VERIFICATION.value
        else:
            final_status = VerificationStatus.REQUIRES_VERIFICATION.value

        # Step 7: Create or Update LandRecord in DB
        existing_record = db.query(LandRecord).filter(LandRecord.document_id == doc.id).first()
        if existing_record:
            record = existing_record
            record.ai_results.clear()
        else:
            record = LandRecord(document_id=doc.id)
            db.add(record)

        # Populate fields
        for field, val in extracted_dict.items():
            setattr(record, field, val)

        record.verification_status = final_status
        record.overall_confidence = overall_conf
        record.validation_flags = json.dumps([v.model_dump() for v in val_flags])
        record.duplicate_info = json.dumps(duplicate_match.model_dump())

        db.commit()
        db.refresh(record)

        # Populate AIResults individual table
        for f_name, f_data in field_scores.items():
            ai_res = AIResult(
                record_id=record.id,
                field_name=f_name,
                extracted_value=f_data.value,
                confidence_score=f_data.confidence,
                confidence_level=f_data.level,
                raw_ocr_confidence=ocr_result.average_confidence,
                validation_status=f_data.status,
                flags=f_data.flag,
            )
            db.add(ai_res)

        # Mark document as processed
        doc.processing_status = ProcessingStatus.PROCESSED.value

        # Add Audit Log
        audit = AuditLog(
            user_id=current_user.id,
            record_id=record.id,
            action="AI_PROCESS_DOCUMENT",
            new_value=f"Processed with overall confidence {overall_conf * 100:.1f}%. Status: {final_status}",
        )
        db.add(audit)
        db.commit()

        return AIProcessingResponse(
            document_id=doc.id,
            record_id=record.id,
            status=final_status,
            overall_confidence=overall_conf,
            fields=field_scores,
            validation_flags=val_flags,
            duplicate_detection=duplicate_match,
            raw_text=ocr_result.raw_text,
            raw_ocr_text=ocr_result.raw_text,
            ocr_status=ocr_result.status,
            ocr_confidence=round(ocr_result.average_confidence, 3),
            ocr_engine_used=ocr_result.engine_used,
            ocr_time_ms=ocr_result.processing_time_ms,
            file_metadata=file_meta,
            father_husband_name=extracted_dict.get("father_husband_name") or extracted_dict.get("father_name"),
            land_area_unit=extracted_dict.get("land_area_unit"),
            preprocessed_image_url=f"/api/documents/{doc.id}/enhanced-file",
            original_image_url=f"/api/documents/{doc.id}/file",
            is_land_record=doc_class_result.is_land_record,
            document_type=doc_class_result.document_type,
            classification_confidence=doc_class_result.confidence,
            warning_message=doc_class_result.warning_message,
            classification_reasons=doc_class_result.reasons,
            is_handwritten=doc_class_result.is_handwritten,
        )

    except Exception as e:
        db.rollback()
        doc.processing_status = ProcessingStatus.FAILED.value
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during AI pipeline execution: {str(e)}",
        )


learner = None


def get_online_learner():
    global learner
    if learner is None:
        from backend.app.ai.online_learner import OnlineContinuousLearner
        learner = OnlineContinuousLearner()
    return learner


@router.post("/adapt", response_model=AdaptationResponse)
def adapt_model_on_realtime_document(
    payload: AdaptationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Online Adaptation Endpoint:
    Trains and updates the AI models on a newly uploaded or verified real-time document
    in < 200ms using Experience Replay Buffer (preventing catastrophic forgetting).
    """
    ol = get_online_learner()
    res = ol.adapt_on_document(
        text=payload.text,
        entities=payload.entities,
        doc_type=payload.doc_type or "user_uploaded_record",
        doc_name=payload.doc_name or "realtime_upload",
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Adaptation failed"))

    # Also adapt document classifier on real-time document
    classifier = get_document_classifier()
    classifier.adapt_realtime(
        text=payload.text,
        is_land_record=True,
        doc_type=payload.doc_type or "user_uploaded_record",
    )
    return res


@router.get("/adaptation-status")
def get_ai_adaptation_status(
    current_user: User = Depends(get_current_user),
):
    """Returns continuous learning status, experience replay buffer health, and latency metrics."""
    ol = get_online_learner()
    return ol.get_adaptation_status()


@router.post("/adapt-sample-9", response_model=AdaptationResponse)
def adapt_model_on_sample_9(
    current_user: User = Depends(get_current_user),
):
    """
    Specialized real-time adaptation on sample_9_estamp_ghaziabad.jpg
    (UP Article 23 Conveyance Deed, Ghaziabad) with experience replay.
    """
    ol = get_online_learner()
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    txt_path = os.path.join(root_dir, "data", "sample_documents", "sample_9_estamp_ghaziabad_ground_truth.txt")
    json_path = os.path.join(root_dir, "data", "sample_records", "sample_9_estamp_ghaziabad.json")

    if not os.path.exists(txt_path) or not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="sample_9_estamp_ghaziabad ground truth files not found")

    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()
    with open(json_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    res = ol.adapt_on_document(
        text=text,
        entities=meta.get("fields", {}),
        doc_type="estamp_conveyance_deed",
        doc_name="sample_9_estamp_ghaziabad.jpg",
    )
    return res

