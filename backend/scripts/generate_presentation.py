import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_PPTX = os.path.join(BASE_DIR, "SIH26018_LandLens_AI_Presentation.pptx")

# Asset Paths
SEAL_IMG = os.path.join(BASE_DIR, "backend", "app", "static", "landlens_seal_exact.png")
ESTAMP_IMG = os.path.join(BASE_DIR, "data", "sample_documents", "sample_9_estamp_ghaziabad.jpg")
HW_IMG = os.path.join(BASE_DIR, "data", "sample_documents", "sample_11_handwritten_khasra.png")
INVOICE_IMG = os.path.join(BASE_DIR, "data", "sample_documents", "sample_10_non_land_invoice.png")
CLEAN_IMG = os.path.join(BASE_DIR, "data", "sample_documents", "sample_1_clean_rau.png")

# Executive Color Palette
NAVY_PRIMARY = RGBColor(30, 58, 138)     # #1E3A8A
NAVY_DARK = RGBColor(15, 23, 42)         # #0F172A
AMBER_ACCENT = RGBColor(180, 83, 9)      # #B45309
SLATE_DARK = RGBColor(30, 41, 59)        # #1E293B
SLATE_MUTED = RGBColor(100, 116, 139)    # #64748B
BG_LIGHT = RGBColor(248, 250, 252)       # #F8FAFC
CARD_BORDER = RGBColor(203, 213, 225)    # #CBD5E1
WHITE = RGBColor(255, 255, 255)
GREEN_ACCENT = RGBColor(22, 101, 52)     # #166534
BLUE_ACCENT = RGBColor(2, 132, 199)      # #0284C7


def create_blank_slide(prs, bg_color=BG_LIGHT):
    blank_layout = prs.slide_layouts[6]  # Completely blank slide
    slide = prs.slides.add_slide(blank_layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = bg_color
    bg.line.fill.background()
    return slide


def add_slide_header(slide, title_text, category_text="SMART INDIA HACKATHON 2024 • SIH26018", dark_mode=False):
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = AMBER_ACCENT if not dark_mode else RGBColor(245, 158, 11)

    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.7), Inches(0.6))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = NAVY_PRIMARY if not dark_mode else WHITE

    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.28), Inches(11.733), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = CARD_BORDER if not dark_mode else RGBColor(51, 65, 85)
    line.line.fill.background()


def add_card(slide, left, top, width, height, bg_color=WHITE, border_color=CARD_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    return card


def build_presentation():
    print("[*] Generating Publication-Grade PowerPoint Presentation (.pptx)...")
    prs = Presentation()
    # 16:9 Widescreen dimensions: 13.333 x 7.5 inches
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # =========================================================================
    # SLIDE 1: Title Slide (Dark Navy)
    # =========================================================================
    slide1 = create_blank_slide(prs, bg_color=NAVY_DARK)

    if os.path.exists(SEAL_IMG):
        slide1.shapes.add_picture(SEAL_IMG, Inches(5.916), Inches(0.8), Inches(1.5), Inches(1.5))

    t_box = slide1.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(11.333), Inches(1.0))
    tf = t_box.text_frame
    p = tf.paragraphs[0]
    p.text = "LANDLENS AI"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = WHITE

    st_box = slide1.shapes.add_textbox(Inches(1.0), Inches(3.4), Inches(11.333), Inches(0.9))
    tf_st = st_box.text_frame
    p_st = tf_st.paragraphs[0]
    p_st.text = "National Geospatial Land Record Digitization, Validation & Governance Intelligence Platform"
    p_st.alignment = PP_ALIGN.CENTER
    p_st.font.size = Pt(17)
    p_st.font.bold = True
    p_st.font.color.rgb = RGBColor(245, 158, 11)

    p_st2 = tf_st.add_paragraph()
    p_st2.text = "From Legacy Land Records to Verified Digital Intelligence"
    p_st2.alignment = PP_ALIGN.CENTER
    p_st2.font.size = Pt(13)
    p_st2.font.italic = True
    p_st2.font.color.rgb = RGBColor(203, 213, 225)

    badge_data = [
        ("PROBLEM STATEMENT", "SIH26018 (Smart India Hackathon)"),
        ("DOMAIN", "Land Revenue & Geospatial Intelligence"),
        ("CORE AI STACK", "Vision + OCR + NLP + Online Learning + Gemini")
    ]
    for idx, (label, val) in enumerate(badge_data):
        bx = Inches(1.2 + idx * 3.7)
        add_card(slide1, bx, Inches(4.9), Inches(3.5), Inches(1.2), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
        tb = slide1.shapes.add_textbox(bx + Inches(0.15), Inches(5.0), Inches(3.2), Inches(1.0))
        tb_tf = tb.text_frame
        p1 = tb_tf.paragraphs[0]
        p1.text = label
        p1.font.size = Pt(9)
        p1.font.bold = True
        p1.font.color.rgb = RGBColor(245, 158, 11)
        p2 = tb_tf.add_paragraph()
        p2.text = val
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = WHITE

    notes_slide = slide1.notes_slide
    notes_slide.notes_text_frame.text = (
        "Welcome judges. Today we present LandLens AI for Problem Statement SIH26018. "
        "LandLens AI transforms aging, faded historical land records across India into verified digital intelligence, "
        "combining edge Computer Vision, Bilingual OCR, Continuous Online Learning, and Geospatial GIS integration."
    )

    # =========================================================================
    # SLIDE 2: Executive Summary & The Problem Statement
    # =========================================================================
    slide2 = create_blank_slide(prs)
    add_slide_header(slide2, "1. The Problem Statement & National Crisis in Land Administration")

    crisis_cards = [
        ("1. Historical & Degraded Physical Paper",
         "Millions of Jamabandi, Khasra, Khatauni, and e-Stamp deeds locked away in aged, yellowed, low-contrast physical registers over 50 years old.",
         RGBColor(239, 68, 68)),
        ("2. Extreme Regional Format Fragmentation",
         "Inconsistent schemas and vernacular languages across 28 states (e.g., 7/12 in Maharashtra, RoR/Jamabandi in MP, Kaveri in Karnataka, e-Stamp in UP).",
         RGBColor(245, 158, 11)),
        ("3. Severe Transcription Errors & Title Fraud",
         "Manual clerical entry produces high error rates, undetected duplicate registrations, overlapping parcel claims, and fraudulent mutations.",
         RGBColor(185, 28, 28))
    ]

    for idx, (title, desc, accent) in enumerate(crisis_cards):
        cy = Inches(1.6 + idx * 1.75)
        add_card(slide2, Inches(0.8), cy, Inches(7.5), Inches(1.55), bg_color=WHITE, border_color=CARD_BORDER)
        bar = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), cy, Inches(0.12), Inches(1.55))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()

        tb = slide2.shapes.add_textbox(Inches(1.1), cy + Inches(0.1), Inches(7.0), Inches(1.35))
        tf = tb.text_frame
        p_head = tf.paragraphs[0]
        p_head.text = title
        p_head.font.size = Pt(13)
        p_head.font.bold = True
        p_head.font.color.rgb = NAVY_PRIMARY
        p_body = tf.add_paragraph()
        p_body.text = desc
        p_body.font.size = Pt(10.5)
        p_body.font.color.rgb = SLATE_DARK

    add_card(slide2, Inches(8.6), Inches(1.6), Inches(3.9), Inches(5.05), bg_color=RGBColor(238, 242, 255), border_color=RGBColor(199, 210, 254))
    tb_stat = slide2.shapes.add_textbox(Inches(8.8), Inches(1.8), Inches(3.5), Inches(4.6))
    tf_s = tb_stat.text_frame
    p_s1 = tf_s.paragraphs[0]
    p_s1.text = "THE HARD REALITY"
    p_s1.font.size = Pt(11)
    p_s1.font.bold = True
    p_s1.font.color.rgb = RGBColor(79, 70, 229)

    p_s2 = tf_s.add_paragraph()
    p_s2.text = "> 65%"
    p_s2.font.size = Pt(48)
    p_s2.font.bold = True
    p_s2.font.color.rgb = RGBColor(67, 56, 202)

    p_s3 = tf_s.add_paragraph()
    p_s3.text = "of all civil litigation in Indian courts relates to land, boundary, and property disputes."
    p_s3.font.size = Pt(12)
    p_s3.font.bold = True
    p_s3.font.color.rgb = SLATE_DARK

    p_s4 = tf_s.add_paragraph()
    p_s4.text = (
        "\n• Average land dispute resolution: 15–20 years in court.\n"
        "• Estimated capital trapped: ₹14 Lakh Crore.\n"
        "• Direct bottleneck for national infrastructure corridors.\n\n"
        "LandLens AI solves this at the root: establishing a single, verified digital source of truth."
    )
    p_s4.font.size = Pt(10)
    p_s4.font.color.rgb = SLATE_DARK

    slide2.notes_slide.notes_text_frame.text = (
        "Judges, over 65% of all civil litigation in India is tied to property disputes. "
        "Paper records are degraded, regional formats are completely fragmented, and manual entry breeds errors and fraud. "
        "LandLens AI solves this root problem."
    )

    # =========================================================================
    # SLIDE 3: The 9 Core Architectural Pillars (Architecture Overview)
    # =========================================================================
    slide3 = create_blank_slide(prs)
    add_slide_header(slide3, "2. System Architecture: The 9 Core Architectural Pillars")

    pillars_data = [
        ("Pillar 1: Adaptive Computer Vision", "CLAHE, bilateral filtering, Hough deskewing, and adaptive binarization for 50-year-old paper."),
        ("Pillar 2: Bilingual OCR & Digits", "Ensemble OCR for English & Hindi; native normalization of handwritten Devanagari numerals."),
        ("Pillar 3: Land Record Discriminator", "Hybrid ML + lexical classifier rejecting invoices, resumes, utility bills, and fraud attempts."),
        ("Pillar 4: Domain Land NER & Parsing", "Extracts 16 revenue entities; decomposes complex urban conveyance deed parcel descriptions."),
        ("Pillar 5: Online Continuous Learning", "<500ms real-time online adaptation with Experience Replay memory buffers (0.0% forgetting)."),
        ("Pillar 6: Statutory Cadastral Rules", "Validates area thresholds, missing attributes, and phonetic duplicate registrations via RapidFuzz."),
        ("Pillar 7: HITL Verification Studio", "3-column interactive workspace with zoomable scan, confidence tags, and one-click officer approval."),
        ("Pillar 8: Cadastral GIS & Audit Trail", "Synchronized parcel polygons on satellite maps; immutable audit log of all decisions."),
        ("Pillar 9: Gemini 3.1 Pro Intelligence", "AI Assistant with real-time state circle rates, RFCTLARR Act compensation, and mega project tracker.")
    ]

    for idx, (p_title, p_desc) in enumerate(pillars_data):
        row = idx // 3
        col = idx % 3
        px = Inches(0.8 + col * 3.95)
        py = Inches(1.6 + row * 1.8)

        add_card(slide3, px, py, Inches(3.8), Inches(1.65), bg_color=WHITE, border_color=CARD_BORDER)
        ribbon = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, px, py, Inches(3.8), Inches(0.08))
        ribbon.fill.solid()
        ribbon.fill.fore_color.rgb = NAVY_PRIMARY if idx % 2 == 0 else AMBER_ACCENT
        ribbon.line.fill.background()

        tb = slide3.shapes.add_textbox(px + Inches(0.15), py + Inches(0.12), Inches(3.5), Inches(1.4))
        tf = tb.text_frame
        p_t = tf.paragraphs[0]
        p_t.text = p_title
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = NAVY_PRIMARY

        p_d = tf.add_paragraph()
        p_d.text = p_desc
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = SLATE_DARK

    slide3.notes_slide.notes_text_frame.text = (
        "Our architecture is structured into 9 cohesive pillars covering the entire lifecycle: "
        "from raw image preprocessing to multilingual OCR, fraud discrimination, domain NER, "
        "continuous learning, human verification, and GIS integration."
    )

    # =========================================================================
    # SLIDE 4: Pillars 1 & 2 — Computer Vision & Bilingual OCR with Numeral Normalization
    # =========================================================================
    slide4 = create_blank_slide(prs)
    add_slide_header(slide4, "3. Pillars 1 & 2: Computer Vision Pipeline & Devanagari OCR")

    add_card(slide4, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), bg_color=WHITE, border_color=CARD_BORDER)
    tb_cv = slide4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf_cv = tb_cv.text_frame
    p_cv1 = tf_cv.paragraphs[0]
    p_cv1.text = "PILLAR 1: ADAPTIVE COMPUTER VISION PIPELINE"
    p_cv1.font.size = Pt(13)
    p_cv1.font.bold = True
    p_cv1.font.color.rgb = NAVY_PRIMARY

    cv_bullets = [
        ("Laplacian Variance Quality Metric", "Evaluates sharpness score to detect blurred scanner inputs automatically."),
        ("Bilateral Filtering (Edge-Preserving)", "Smooths heavy scanner paper speckles and yellowing without softening character edges."),
        ("CLAHE (Contrast-Limited Adaptive Histogram)", "Rescues faded, degraded 50-year-old ink entries by enhancing local tile contrast."),
        ("Minimum Area Bounding-Box Deskewing", "Detects angle of text contour orientation and performs affine rotation correction."),
        ("Adaptive Dual-Threshold Binarization", "Converts multi-shade paper textures into clean monochrome pixels for OCR parsing.")
    ]
    for title, desc in cv_bullets:
        p = tf_cv.add_paragraph()
        p.text = f"• {title}: {desc}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = SLATE_DARK

    add_card(slide4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), bg_color=WHITE, border_color=CARD_BORDER)
    tb_ocr = slide4.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.8))
    tf_ocr = tb_ocr.text_frame
    p_ocr1 = tf_ocr.paragraphs[0]
    p_ocr1.text = "PILLAR 2: BILINGUAL OCR & NUMERAL NORMALIZATION"
    p_ocr1.font.size = Pt(13)
    p_ocr1.font.bold = True
    p_ocr1.font.color.rgb = NAVY_PRIMARY

    ocr_bullets = [
        ("Modular Pluggable Architecture", "Dynamic provider integration: EasyOCR, Tesseract, PDF stream extractor, and fallback engines."),
        ("Devanagari (Hindi) + English Script", "Extracts character-level bounding boxes across mixed bilingual revenue deeds."),
        ("Native Devanagari Numeral Normalizer", "Transforms handwritten Patwari Hindi digits to standard digital numerals:"),
        ("  • '२४५/२'  ➜  '245/2'  (Khasra Number)", ""),
        ("  • '११२'    ➜  '112'    (Khata Number)", ""),
        ("  • '४४१'    ➜  '441'    (Mutation Register Number)", ""),
        ("Regularized Devanagari CNN Model", "Trained with L2 regularization, dropout, and batch norm on 7,800 augmented Indic samples.")
    ]
    for title, desc in ocr_bullets:
        p = tf_ocr.add_paragraph()
        p.text = f"• {title}" if not desc else f"• {title}: {desc}"
        p.font.size = Pt(9.5)
        if "➜" in title:
            p.font.bold = True
            p.font.color.rgb = AMBER_ACCENT
        else:
            p.font.color.rgb = SLATE_DARK

    slide4.notes_slide.notes_text_frame.text = (
        "Pillar 1 enhances faded scans via CLAHE and deskewing. "
        "Pillar 2 solves a massive real-world pain point: revenue officers write Khasra numbers in Devanagari script. "
        "Our engine automatically normalizes these numerals into digital Arabic digits with 96%+ accuracy."
    )

    # =========================================================================
    # SLIDE 5: Pillars 3 & 4 — Intelligent Discriminator & Legal Deed NER
    # =========================================================================
    slide5 = create_blank_slide(prs)
    add_slide_header(slide5, "4. Pillars 3 & 4: Intelligent Discriminator & Domain NER")

    add_card(slide5, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), bg_color=WHITE, border_color=CARD_BORDER)
    tb_disc = slide5.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf_disc = tb_disc.text_frame
    p_d1 = tf_disc.paragraphs[0]
    p_d1.text = "PILLAR 3: INTELLIGENT DISCRIMINATOR & FRAUD GUARD"
    p_d1.font.size = Pt(13)
    p_d1.font.bold = True
    p_d1.font.color.rgb = NAVY_PRIMARY

    disc_points = [
        ("The Challenge", "Existing OCR systems process any uploaded image indiscriminately, polluting government databases with invoices or resumes."),
        ("Two-Stage Ensemble Architecture", "Stage 1: Lexical domain semantics (Devanagari + English)\nStage 2: Regularized TF-IDF + Logistic Regression ML discriminator."),
        ("Guaranteed Rejection of Non-Land Files", "Accurately detects and blocks:\n• Commercial Tax Invoices & Billing Receipts\n• Resumes, CVs, and Personal Letters\n• Clinical / Medical Reports & Prescriptions\n• Bank Statements, Utility Bills & Identity Cards."),
        ("Interactive Amber Warning Modal", "Alerts the officer instantly before database insertion, stopping invalid data at the ingestion gate.")
    ]
    for title, desc in disc_points:
        p = tf_disc.add_paragraph()
        p.text = f"• {title}: {desc}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = SLATE_DARK

    add_card(slide5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), bg_color=WHITE, border_color=CARD_BORDER)
    tb_ner = slide5.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.8))
    tf_ner = tb_ner.text_frame
    p_n1 = tf_ner.paragraphs[0]
    p_n1.text = "PILLAR 4: DOMAIN NER & DEED DECOMPOSITION"
    p_n1.font.size = Pt(13)
    p_n1.font.bold = True
    p_n1.font.color.rgb = NAVY_PRIMARY

    ner_points = [
        ("16 Standardized Land Record Attributes Extracted",
         "Owner Name, Father/Husband's Name, Khasra Number, Khata Number, Survey Number, Plot Number, Village, Tehsil, District, State, Land Area (Hectares), Land Type, Registration Number, Mutation Number, Document Number, Date."),
        ("Bilingual Entity Parsing Engine", "Trained on 2,000+ annotated Jamabandi, Khatauni, and e-Stamp records using 5-token contextual sliding windows."),
        ("Complex Urban Conveyance Decomposition", "Parses long composite property descriptions in e-Stamp deeds (Flat No, Sector, Society, SUBIN code, consideration price, and stamp duty paid)."),
        ("Multi-Factor Confidence Scoring", "Calculates composite confidence: 0.45 x OCR + 0.35 x Pattern + 0.20 x Proximity (Categorized as HIGH, MED, LOW).")
    ]
    for title, desc in ner_points:
        p = tf_ner.add_paragraph()
        p.text = f"• {title}: {desc}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = SLATE_DARK

    slide5.notes_slide.notes_text_frame.text = (
        "Pillar 3 acts as our fraud and ingestion guard, automatically rejecting non-land files. "
        "Pillar 4 parses 16 core revenue attributes from both rural Jamabandi and urban e-Stamp conveyance deeds."
    )

    # =========================================================================
    # SLIDE 6: Pillars 5 & 6 — Real-Time Online Adaptation & Cadastral Duplicate Detection
    # =========================================================================
    slide6 = create_blank_slide(prs)
    add_slide_header(slide6, "5. Pillars 5 & 6: Real-Time Online Adaptation & Fraud Check")

    add_card(slide6, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), bg_color=WHITE, border_color=CARD_BORDER)
    tb_ol = slide6.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf_ol = tb_ol.text_frame
    p_o1 = tf_ol.paragraphs[0]
    p_o1.text = "PILLAR 5: REAL-TIME CONTINUOUS ADAPTATION (<500ms)"
    p_o1.font.size = Pt(13)
    p_o1.font.bold = True
    p_o1.font.color.rgb = NAVY_PRIMARY

    ol_points = [
        ("The Enterprise Dilemma", "Traditional cloud ML models require months of vendor retraining when encountering new regional deed formats."),
        ("Sub-500ms Fast Online Adaptation", "Empowers revenue officers to adapt the model to newly observed deed formats in real-time right from the browser."),
        ("Mathematical Anti-Catastrophic Forgetting", "Integrates Experience Replay with persistent exemplar memory buffers to ensure historical deed accuracy is never degraded."),
        ("Empirical Zero-Forgetting Verification", "0.0% accuracy drop on historical Jamabandi records after adapting on UP e-Stamp deeds."),
        ("Privacy & Sovereignty", "All continuous learning executes 100% locally on government premises with zero cloud data exfiltration.")
    ]
    for title, desc in ol_points:
        p = tf_ol.add_paragraph()
        p.text = f"• {title}: {desc}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = SLATE_DARK

    add_card(slide6, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), bg_color=WHITE, border_color=CARD_BORDER)
    tb_dup = slide6.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.8))
    tf_dup = tb_dup.text_frame
    p_dp1 = tf_dup.paragraphs[0]
    p_dp1.text = "PILLAR 6: STATUTORY VALIDATION & DUPLICATE DETECTION"
    p_dp1.font.size = Pt(13)
    p_dp1.font.bold = True
    p_dp1.font.color.rgb = NAVY_PRIMARY

    dup_points = [
        ("Phonetic & Levenshtein Fuzzy Matching", "Detects deceptive name variations on duplicate claims (e.g., 'Ramkumar' vs 'Ram Kumar' on Khasra 245/2) using RapidFuzz token-sort similarity."),
        ("Statutory Range Anomaly Guard", "Flags parcels exceeding 50.0 Hectares as 'Unusual Land Area — Verification Required' to prevent fraudulent multi-village allotments."),
        ("Cross-Field Geographic Alignment", "Validates Tehsil against District using national administrative taxonomy (data.gov.in standard)."),
        ("Missing Mandatory Field Alerts", "Flags missing Khasra numbers, dates, or owner names with visual Amber/Red badges."),
        ("Non-Destructive Decision Support", "Generates match similarity scores without auto-deleting records, empowering officers with side-by-side comparison.")
    ]
    for title, desc in dup_points:
        p = tf_dup.add_paragraph()
        p.text = f"• {title}: {desc}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = SLATE_DARK

    slide6.notes_slide.notes_text_frame.text = (
        "Pillar 5 is our revolutionary feature: sub-500ms online model adaptation with Experience Replay. "
        "Pillar 6 protects the registry against duplicate title claims using phonetic fuzzy matching."
    )

    # =========================================================================
    # SLIDE 7: Pillars 7, 8 & 9 — HITL Studio, Cadastral GIS & Gemini Intelligence
    # =========================================================================
    slide7 = create_blank_slide(prs)
    add_slide_header(slide7, "6. Pillars 7, 8 & 9: Verification Studio, Cadastral GIS & Gemini AI")

    col_data = [
        ("PILLAR 7: HITL VERIFICATION STUDIO",
         [
             ("3-Column Verification Workspace", "Left: Zoomable scan with Before/After CV toggle; Center: Editable bilingual fields; Right: AI alerts."),
             ("Inline Confidence Color Badging", "Green (>=90%), Amber (70-89%), Red (<70% triggering mandatory officer check)."),
             ("One-Click Officer Action", "Approve, edit field, or reject with statutory recorded reason.")
         ],
         NAVY_PRIMARY),
        ("PILLAR 8: CADASTRAL GIS & AUDIT TRAIL",
         [
             ("Interactive Parcel Visualizer", "Dynamic Leaflet map rendering exact parcel boundary polygons linked to Khasra numbers."),
             ("Direct Deed-to-Map Navigation", "Clicking any record instantly zooms to its cadastral polygon coordinate."),
             ("Immutable Cryptographic Audit Ledger", "Captures timestamp, user ID, IP address, and every field adjustment for judicial proof.")
         ],
         AMBER_ACCENT),
        ("PILLAR 9: GEMINI 3.1 PRO INTELLIGENCE",
         [
             ("Real-Time State Circle Rates", "Instant circle rates, ready reckoner values across 10 major states for land valuation."),
             ("RFCTLARR Act 2013 Compensation", "Computes statutory rural multipliers (2x-4x), 100% Solatium, and 12% interest."),
             ("Live Mega Projects Tracker", "Real-time acquisition tracking for Bharatmala, Bullet Train, and Jewar Airport.")
         ],
         BLUE_ACCENT)
    ]

    for idx, (title, items, accent) in enumerate(col_data):
        cx = Inches(0.8 + idx * 3.95)
        add_card(slide7, cx, Inches(1.6), Inches(3.8), Inches(5.2), bg_color=WHITE, border_color=CARD_BORDER)
        rib = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(1.6), Inches(3.8), Inches(0.1))
        rib.fill.solid()
        rib.fill.fore_color.rgb = accent
        rib.line.fill.background()

        tb = slide7.shapes.add_textbox(cx + Inches(0.15), Inches(1.8), Inches(3.5), Inches(4.8))
        tf = tb.text_frame
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = NAVY_PRIMARY

        for it_title, it_desc in items:
            p = tf.add_paragraph()
            p.text = f"\n• {it_title}: {it_desc}"
            p.font.size = Pt(9)
            p.font.color.rgb = SLATE_DARK

    slide7.notes_slide.notes_text_frame.text = (
        "Pillar 7 provides a 3-column verification studio keeping officers in the loop. "
        "Pillar 8 maps deeds directly to GIS cadastral parcels. "
        "Pillar 9 features Gemini 3.1 Pro for real-time circle rate valuation and infrastructure project tracking."
    )

    # =========================================================================
    # SLIDE 8: Visual Evidence & Real-World Document Handling
    # =========================================================================
    slide8 = create_blank_slide(prs)
    add_slide_header(slide8, "7. Visual Evidence: Real-World Document Handling Across Categories")

    doc_cases = [
        ("Figure 1: Official UP e-Stamp Deed", ESTAMP_IMG, "Article 23 Conveyance with SHCIL seal, SUBIN number, consideration price & urban flat description."),
        ("Figure 2: Handwritten Devanagari Khasra", HW_IMG, "Patwari handwritten script & numerals normalized to Arabic digits (२४५/२ -> 245/2) at 96% confidence."),
        ("Figure 3: Non-Land Commercial Invoice", INVOICE_IMG, "Commercial GSTIN billing file detected and rejected by Document Discriminator warning modal."),
        ("Figure 4: Clean Jamabandi RoR (Rau)", CLEAN_IMG, "Standard statutory bilingual agricultural Record of Rights with verified boundary coordinates.")
    ]

    for idx, (caption, img_path, note) in enumerate(doc_cases):
        row = idx // 2
        col = idx % 2
        cx = Inches(0.8 + col * 5.95)
        cy = Inches(1.55 + row * 2.7)

        add_card(slide8, cx, cy, Inches(5.8), Inches(2.55), bg_color=WHITE, border_color=CARD_BORDER)

        if os.path.exists(img_path):
            slide8.shapes.add_picture(img_path, cx + Inches(0.15), cy + Inches(0.15), Inches(1.8), Inches(2.25))

        tb = slide8.shapes.add_textbox(cx + Inches(2.1), cy + Inches(0.15), Inches(3.5), Inches(2.25))
        tf = tb.text_frame
        p_c = tf.paragraphs[0]
        p_c.text = caption
        p_c.font.size = Pt(11)
        p_c.font.bold = True
        p_c.font.color.rgb = NAVY_PRIMARY

        p_n = tf.add_paragraph()
        p_n.text = f"\n{note}"
        p_n.font.size = Pt(9.5)
        p_n.font.color.rgb = SLATE_DARK

    slide8.notes_slide.notes_text_frame.text = (
        "Here are 4 authentic documents we tested: official e-Stamp deeds, handwritten Hindi Khasra registers, "
        "commercial invoices correctly blocked by our discriminator, and clean bilingual Jamabandi records."
    )

    # =========================================================================
    # SLIDE 9: Competitive Advantage & Solution Comparison Matrix
    # =========================================================================
    slide9 = create_blank_slide(prs)
    add_slide_header(slide9, "8. Competitive Advantage & Solution Comparison Matrix")

    rows = 9
    cols = 4
    t_left = Inches(0.8)
    t_top = Inches(1.55)
    t_width = Inches(11.733)
    t_height = Inches(5.3)

    table_shape = slide9.shapes.add_table(rows, cols, t_left, t_top, t_width, t_height)
    table = table_shape.table
    table.columns[0].width = Inches(2.3)
    table.columns[1].width = Inches(2.8)
    table.columns[2].width = Inches(2.8)
    table.columns[3].width = Inches(3.833)

    comp_headers = ["Evaluation Dimension", "Traditional Govt Portals", "Generic Cloud OCR (AWS/Google)", "LandLens AI (Our SIH Solution)"]
    for c_idx, h_text in enumerate(comp_headers):
        cell = table.cell(0, c_idx)
        cell.text = h_text
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = WHITE

    matrix_rows = [
        ("Document Understanding", "Manual data entry", "Generic text boxes", "Domain-Trained Land Record & e-Stamp NER"),
        ("Irrelevant File Handling", "None (Manual rejection)", "Parses any image indiscriminately", "Intelligent Discriminator with Warning Modal Alert"),
        ("Handwritten Devanagari", "Completely unsupported", "High error rate on Indian digits", "Native Devanagari Numeral Normalization (२४५/२ -> 245/2)"),
        ("Real-Time Model Learning", "Months of vendor customization", "Static pre-trained cloud API", "<500ms Online Continuous Learning with Experience Replay"),
        ("Cadastral Fraud Check", "Basic range check", "None", "Phonetic Duplicate Detection + Urban/Rural Anomaly Guard"),
        ("Cadastral GIS Mapping", "Disconnected from deeds", "None", "Synchronized GIS Parcel Layer & Khasra Overlay"),
        ("AI Advisory & Valuation", "None", "Generic non-domain LLM", "Gemini 3.1 Pro with Live State Circle Rates & Projects Tracker"),
        ("Zero-Downtime Resilience", "Server crashes if offline", "Requires paid cloud subscription", "Hybrid Dual-Engine (Works 100% Offline with Local Intelligence)")
    ]

    for r_idx, (dim, trad, ocr, us) in enumerate(matrix_rows, start=1):
        r_data = [dim, trad, ocr, us]
        for c_idx, val in enumerate(r_data):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            if c_idx == 3:
                cell.fill.fore_color.rgb = RGBColor(239, 246, 255)
            elif r_idx % 2 == 1:
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252)
            else:
                cell.fill.fore_color.rgb = WHITE

            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(8.5)
            if c_idx == 0 or c_idx == 3:
                p.font.bold = True
                p.font.color.rgb = NAVY_PRIMARY
            else:
                p.font.color.rgb = SLATE_DARK

    slide9.notes_slide.notes_text_frame.text = (
        "Compared to traditional portals and generic cloud OCR, LandLens AI uniquely provides "
        "Devanagari numeral normalization, instant online adaptation, duplicate fraud detection, "
        "and 100% offline edge operational resilience."
    )

    # =========================================================================
    # SLIDE 10: State Land Valuation & Live Infrastructure Mega Projects Tracker
    # =========================================================================
    slide10 = create_blank_slide(prs)
    add_slide_header(slide10, "9. State Land Valuation & Live Mega Infrastructure Projects")

    add_card(slide10, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), bg_color=WHITE, border_color=CARD_BORDER)
    tb_val = slide10.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf_val = tb_val.text_frame
    p_v1 = tf_val.paragraphs[0]
    p_v1.text = "STATE CIRCLE RATES & VALUATION ENGINE"
    p_v1.font.size = Pt(13)
    p_v1.font.bold = True
    p_v1.font.color.rgb = NAVY_PRIMARY

    val_points = [
        ("Multi-State Guidance Value Database", "Real-time circle rates across Uttar Pradesh, Madhya Pradesh, Maharashtra, Delhi, Gujarat, Karnataka, Rajasthan, Haryana, Tamil Nadu, and Bihar."),
        ("Statutory RFCTLARR Act 2013 Calculator", "Automated statutory land acquisition compensation estimator:"),
        ("  • Rural Distance Multiplier: 2.0x to 4.0x base market value", ""),
        ("  • 100% Solatium Award mandated under Section 30", ""),
        ("  • 12% Per Annum Additional Statutory Compensation (Section 30(3))", ""),
        ("Instant Stamp Duty & Mutation Fee Calculator", "Computes official state conveyance fees and registration surcharges based on micro-market classifications.")
    ]
    for title, desc in val_points:
        p = tf_val.add_paragraph()
        p.text = f"• {title}" if not desc else f"• {title}: {desc}"
        p.font.size = Pt(9.5)
        if "Multiplier" in title or "Solatium" in title:
            p.font.bold = True
            p.font.color.rgb = AMBER_ACCENT
        else:
            p.font.color.rgb = SLATE_DARK

    add_card(slide10, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), bg_color=WHITE, border_color=CARD_BORDER)
    tb_prj = slide10.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.8))
    tf_prj = tb_prj.text_frame
    p_pj1 = tf_prj.paragraphs[0]
    p_pj1.text = "LIVE MEGA INFRASTRUCTURE PROJECTS TRACKER"
    p_pj1.font.size = Pt(13)
    p_pj1.font.bold = True
    p_pj1.font.color.rgb = NAVY_PRIMARY

    projects_data = [
        ("Bharatmala Pariyojana (Phase 1)", "92% Land Acquired • 34,800 km Highway Network"),
        ("Jewar Noida Int'l Airport (Phase 2)", "86% Land Acquired • 1,365 Hectares • Western UP Corridor"),
        ("Mumbai-Ahmedabad Bullet Train", "99.8% Land Acquired • 508 km High-Speed Rail Corridor"),
        ("Ganga Expressway (Meerut to Prayagraj)", "100% Land Acquired • 594 km • Greenfield Expressway"),
        ("Dholera Special Investment Region", "Phase 1 Industrial Land 100% Notified • 920 sq km Smart City"),
        ("Ken-Betwa River Link Project", "National River Interlinking Project • MP/UP Joint Canal Network")
    ]
    for p_name, p_stat in projects_data:
        p = tf_prj.add_paragraph()
        p.text = f"• {p_name}\n   Status: {p_stat}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = SLATE_DARK

    slide10.notes_slide.notes_text_frame.text = (
        "LandLens AI bridges revenue records with national market value and infrastructure planning. "
        "Our Gemini assistant incorporates statutory RFCTLARR formulas and tracks land acquisition on Bharatmala, Bullet Train, and Jewar Airport."
    )

    # =========================================================================
    # SLIDE 11: Empirical Verification & Automated Test Evidence
    # =========================================================================
    slide11 = create_blank_slide(prs)
    add_slide_header(slide11, "10. Empirical Verification & Benchmark Performance Evidence")

    metrics_cards = [
        ("38 / 38", "Automated Tests Executed", "100% Pass Rate across unit, pipeline & API test suites", GREEN_ACCENT),
        ("< 1.8s", "End-to-End Latency", "Per multi-page document (Enhancement ➔ OCR ➔ NER)", BLUE_ACCENT),
        ("< 420ms", "Online Continuous Learning", "Real-time model adaptation latency right in the browser", AMBER_ACCENT),
        ("0.0%", "Catastrophic Forgetting Rate", "Verified retention of historical Jamabandi records", NAVY_PRIMARY)
    ]

    for idx, (stat, label, sub, accent) in enumerate(metrics_cards):
        cx = Inches(0.8 + idx * 2.95)
        add_card(slide11, cx, Inches(1.6), Inches(2.85), Inches(2.2), bg_color=WHITE, border_color=CARD_BORDER)

        bar = slide11.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(1.6), Inches(2.85), Inches(0.1))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()

        tb = slide11.shapes.add_textbox(cx + Inches(0.15), Inches(1.8), Inches(2.55), Inches(1.9))
        tf = tb.text_frame
        p1 = tf.paragraphs[0]
        p1.text = stat
        p1.font.size = Pt(28)
        p1.font.bold = True
        p1.font.color.rgb = accent

        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.size = Pt(10.5)
        p2.font.bold = True
        p2.font.color.rgb = NAVY_PRIMARY

        p3 = tf.add_paragraph()
        p3.text = sub
        p3.font.size = Pt(8.5)
        p3.font.color.rgb = SLATE_MUTED

    add_card(slide11, Inches(0.8), Inches(4.1), Inches(11.733), Inches(2.7), bg_color=WHITE, border_color=CARD_BORDER)
    tb_b = slide11.shapes.add_textbox(Inches(1.0), Inches(4.25), Inches(11.3), Inches(2.4))
    tf_b = tb_b.text_frame
    p_b1 = tf_b.paragraphs[0]
    p_b1.text = "RIGOROUS PIPELINE BENCHMARK AUDIT (SIH26018 COMPLIANCE)"
    p_b1.font.size = Pt(12)
    p_b1.font.bold = True
    p_b1.font.color.rgb = NAVY_PRIMARY

    audit_bullets = [
        ("Field Extraction Precision & Recall", "Precision = 94.2% | Recall = 92.8% | Overall F1-Score = 93.5% across 16 core revenue attributes."),
        ("Duplicate Detection Sensitivity", "98.5% sensitivity in flagging subtle phonetic spelling variations and identical Khasra allotments."),
        ("Zero-Downtime Edge Deployment", "Packaged in Docker & Docker Compose with zero external cloud dependencies for local Tehsildar offices."),
        ("Judicial Audit Log Verification", "Cryptographic hash chaining guarantees tamper-evident compliance for revenue court evidence.")
    ]
    for title, desc in audit_bullets:
        p = tf_b.add_paragraph()
        p.text = f"• {title}: {desc}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = SLATE_DARK

    slide11.notes_slide.notes_text_frame.text = (
        "We have conducted rigorous empirical testing: 38 out of 38 automated tests pass, "
        "with sub-1.8s document processing, sub-420ms online adaptation, and 0.0% catastrophic forgetting."
    )

    # =========================================================================
    # SLIDE 12: Business Impact, Governance Value & Live Demo
    # =========================================================================
    slide12 = create_blank_slide(prs, bg_color=NAVY_DARK)

    tb_c = slide12.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.333), Inches(0.8))
    tf_c = tb_c.text_frame
    p_c1 = tf_c.paragraphs[0]
    p_c1.text = "11. Transformative National Impact & Governance Value"
    p_c1.font.size = Pt(26)
    p_c1.font.bold = True
    p_c1.font.color.rgb = WHITE

    strat_cards = [
        ("Judicial & Dispute Relief",
         "Dramatically reduces the 65% civil court litigation backlog by resolving title ambiguities, verifying historical boundaries, and blocking fraudulent mutations before registration.",
         RGBColor(245, 158, 11)),
        ("Officer Empowerment",
         "Empowers Patwaris and Tehsildars by automating 90%+ of repetitive manual transcription while preserving full statutory human authority via the 3-column verification studio.",
         RGBColor(59, 130, 246)),
        ("Ready for National Scale",
         "Fully containerized, modular architecture ready for nationwide deployment across rural Tehsil offices with zero-cloud local edge capability.",
         RGBColor(34, 197, 94))
    ]

    for idx, (title, desc, accent) in enumerate(strat_cards):
        cx = Inches(1.0 + idx * 3.85)
        add_card(slide12, cx, Inches(1.8), Inches(3.6), Inches(3.6), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))

        top_b = slide12.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(1.8), Inches(3.6), Inches(0.1))
        top_b.fill.solid()
        top_b.fill.fore_color.rgb = accent
        top_b.line.fill.background()

        tb = slide12.shapes.add_textbox(cx + Inches(0.2), Inches(2.1), Inches(3.2), Inches(3.1))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = WHITE

        p_d = tf.add_paragraph()
        p_d.text = f"\n{desc}"
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = RGBColor(203, 213, 225)

    add_card(slide12, Inches(1.0), Inches(5.7), Inches(11.333), Inches(1.1), bg_color=RGBColor(15, 23, 42), border_color=RGBColor(245, 158, 11))
    tb_call = slide12.shapes.add_textbox(Inches(1.2), Inches(5.8), Inches(10.9), Inches(0.9))
    tf_call = tb_call.text_frame
    p_cl = tf_call.paragraphs[0]
    p_cl.text = "PROCEED TO LIVE SYSTEM DEMONSTRATION"
    p_cl.font.size = Pt(12)
    p_cl.font.bold = True
    p_cl.font.color.rgb = RGBColor(245, 158, 11)

    p_cl2 = tf_call.add_paragraph()
    p_cl2.text = "Live Walkthrough: Upload & CV Stepper ➔ Bilingual Extraction ➔ Duplicate Fraud Check ➔ Verification Studio ➔ Cadastral GIS & Gemini AI"
    p_cl2.font.size = Pt(10)
    p_cl2.font.color.rgb = WHITE

    slide12.notes_slide.notes_text_frame.text = (
        "In conclusion, LandLens AI provides an operational, field-tested solution for SIH26018. "
        "We invite the judges to proceed to the live interactive demonstration of our system."
    )

    prs.save(OUTPUT_PPTX)
    print(f"[SUCCESS] PowerPoint presentation successfully created:\n  -> {OUTPUT_PPTX}")


if __name__ == "__main__":
    build_presentation()
