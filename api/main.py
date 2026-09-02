"""
FastAPI Main Application Entry Point for AI Perception Service
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
Target Integration:
- Vinit's Central Case API (Upstream producer & store)
- Aatmman's Agentic Decision Layer (Downstream consumer)
==============================================================================
"""

import time
import torch
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse

from api.middleware.request_id import RequestIDMiddleware
from api.routes.perception_routes import router as perception_router, get_perception_service
from api.routes.analytics_routes import router as analytics_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager: Pre-loads ML models once during startup."""
    print("=" * 80)
    print("Starting NHAA 14566 / SIH 26093 - AI Perception Layer FastAPI Service")
    print("=" * 80)
    
    # Pre-load ML models into RAM/GPU memory once
    service = get_perception_service()
    app.state.perception_service = service
    
    yield
    
    print("[Shutdown] Cleaning up AI Perception Layer resources...")

app = FastAPI(
    title="NHAA 14566 / SIH 26093 - AI Perception Layer API",
    description=(
        "Production-ready FastAPI service providing Multilingual Speech-to-Text (Whisper), "
        "Acoustic Feature Extraction, Speech Emotion Recognition (Wav2Vec2), "
        "Multilingual Text Distress Classification (MuRIL/IndicBERT), "
        "Explainable Evidence Generation, Stress Vulnerability Index (SVI 0-100) Fusion, "
        "and Perception Analytics Endpoints."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Mount Middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API Routers
app.include_router(perception_router)
app.include_router(analytics_router)


@app.get("/", tags=["System Information"], summary="Root API Information & Docs Redirect")
async def root():
    """Returns welcome landing page metadata and documentation links."""
    return {
        "title": "NHAA 14566 / SIH 26093 - AI Perception Layer API",
        "status": "online",
        "documentation": "/docs",
        "interactive_voice_tester": "/upload-test",
        "redoc": "/redoc",
        "health_check": "/health",
        "perception_analyze_endpoint": "/api/v1/perception/analyze"
    }


@app.get("/upload-test", response_class=HTMLResponse, tags=["Testing UI"], summary="Interactive Audio File Testing UI")
async def upload_test_ui():
    """Renders a simple HTML Audio File Test Page for uploading and analyzing recorded voice files."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>NHAA AI Perception - Audio Voice Tester</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }
            .container { max-width: 800px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
            h1 { color: #38bdf8; margin-top: 0; }
            p { color: #94a3b8; }
            .form-group { margin-bottom: 20px; }
            label { display: block; font-weight: bold; margin-bottom: 8px; color: #e2e8f0; }
            input[type="file"], select, input[type="text"] { width: 100%; padding: 12px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #f8fafc; box-sizing: border-box; }
            button { background: #0284c7; color: white; border: none; padding: 14px 28px; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; width: 100%; transition: background 0.2s; }
            button:hover { background: #0369a1; }
            #result { margin-top: 30px; background: #0f172a; padding: 20px; border-radius: 8px; border: 1px solid #334155; white-space: pre-wrap; font-family: monospace; font-size: 14px; max-height: 400px; overflow-y: auto; display: none; }
            .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase; background: #38bdf8; color: #0f172a; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎙️ NHAA AI Perception - Audio Voice Tester</h1>
            <p>Upload any recorded <code>.mp3</code> or <code>.wav</code> voice file below to analyze STT transcript, pitch, pauses, emotion, and SVI Risk Score live.</p>
            
            <form id="voiceForm">
                <div class="form-group">
                    <label for="audio">Select Spoken Audio Voice File (.mp3, .wav, .m4a):</label>
                    <input type="file" id="audio" name="audio" accept="audio/*" required>
                </div>

                <div class="form-group">
                    <label for="language">Select Language:</label>
                    <select id="language" name="language">
                        <option value="hi">Hindi (hi)</option>
                        <option value="mr">Marathi (mr)</option>
                        <option value="en">English (en)</option>
                        <option value="ta">Tamil (ta)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="channel">Helpline Ingestion Channel:</label>
                    <select id="channel" name="channel">
                        <option value="ivrs">IVRS Telephonic Call</option>
                        <option value="mobile_app">Mobile App</option>
                        <option value="phone">Helpline Phone Call</option>
                    </select>
                </div>

                <button type="submit" id="submitBtn">⚡ Analyze Audio Perception Live</button>
            </form>

            <div id="result"></div>
        </div>

        <script>
            document.getElementById('voiceForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const btn = document.getElementById('submitBtn');
                const resultDiv = document.getElementById('result');
                btn.disabled = true;
                btn.innerText = "⏳ Processing Audio via GPU Neural Models...";
                resultDiv.style.display = "block";
                resultDiv.innerText = "Analyzing audio... Please wait...";

                const formData = new FormData(e.target);

                try {
                    const response = await fetch('/api/v1/perception/analyze', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    btn.disabled = false;
                    btn.innerText = "⚡ Analyze Audio Perception Live";
                    resultDiv.innerText = JSON.stringify(data, null, 2);
                } catch (err) {
                    btn.disabled = false;
                    btn.innerText = "⚡ Analyze Audio Perception Live";
                    resultDiv.innerText = "Error: " + err.message;
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get(
    "/health",
    tags=["Health Check"],
    summary="Service Health Check Endpoint",
    description="Returns health status, GPU availability, and model loading status."
)
async def health_check():
    """Health check endpoint for container orchestrators and load balancers."""
    gpu_available = torch.cuda.is_available()
    service = getattr(app.state, "perception_service", None)
    models_loaded = service.models_loaded if service else False

    return {
        "status": "healthy",
        "timestamp": round(time.time(), 3),
        "version": "1.0.0",
        "gpu_available": gpu_available,
        "models_loaded": models_loaded,
        "device": "cuda" if gpu_available else "cpu"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler ensuring clean JSON error responses."""
    print(f"[API UNHANDLED EXCEPTION] {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error occurred in AI Perception Layer.",
            "error_summary": str(exc)
        }
    )
