import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.database.init_db import init_db
from backend.app.api import auth, documents, ai_process, records, dashboard, audit, gis, chatbot

app = FastAPI(
    title="LandLens AI — Intelligent Land Record Digitization & Validation System",
    description="Smart India Hackathon (SIH26018) Backend API with CV, OCR, NLP, Confidence Scoring, Validation, Duplicate Detection, and Verification.",
    version="1.0.0",
)

# CORS Configuration for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database, AI Models, and Demo Assets
def initialize_system():
    init_db()
    try:
        from backend.app.ai.online_learner import OnlineContinuousLearner
        OnlineContinuousLearner()
    except Exception:
        pass
    try:
        from backend.app.ai.document_classifier import get_document_classifier
        get_document_classifier()
    except Exception:
        pass
    try:
        sample_docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_documents"))
        inv_png = os.path.join(sample_docs_dir, "sample_10_non_land_invoice.png")
        hand_png = os.path.join(sample_docs_dir, "sample_11_handwritten_khasra.png")
        if not os.path.exists(inv_png) or not os.path.exists(hand_png):
            from backend.scripts.generate_samples import _render_invoice_image, _render_handwritten_khasra_image
            if not os.path.exists(inv_png):
                _render_invoice_image(inv_png)
            if not os.path.exists(hand_png):
                _render_handwritten_khasra_image(hand_png)
    except Exception:
        pass

# Run initialization immediately on load to ensure assets exist
initialize_system()

@app.on_event("startup")
def on_startup():
    initialize_system()


# Include Routers
app.include_router(auth.router)
app.include_router(ai_process.router)
app.include_router(documents.router)
app.include_router(records.router)
app.include_router(dashboard.router)
app.include_router(audit.router)
app.include_router(gis.router)
app.include_router(chatbot.router)

# Mount Uploads directory for document files
uploads_dir = os.path.abspath(os.getenv("UPLOAD_DIR", "./uploads"))
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Mount sample documents for demo quick-upload
sample_docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_documents"))
if os.path.exists(sample_docs_dir):
    app.mount("/sample-data", StaticFiles(directory=sample_docs_dir), name="sample-data")

# Mount Static Frontend Directory
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
os.makedirs(static_dir, exist_ok=True)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "LandLens AI"}

@app.get("/app.js")
def serve_app_js():
    js_file = os.path.join(static_dir, "app.js")
    if os.path.exists(js_file):
        return FileResponse(js_file, media_type="application/javascript")
    return {"error": "app.js not found"}

@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "message": "LandLens AI API is running. Access API documentation at /docs",
        "docs_url": "/docs",
        "health": "OK",
    }

app.mount("/static", StaticFiles(directory=static_dir), name="static")
