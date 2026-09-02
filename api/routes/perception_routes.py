"""
FastAPI Route Handlers for AI Perception Service Endpoints
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
Exposes RESTful endpoints for speech-to-text, speech emotion recognition,
acoustic analysis, text distress classification, and SVI score fusion.
==============================================================================
"""

import time
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Request, status
from fastapi.responses import JSONResponse

from perception.schemas import PerceptionOutputContract
from api.services.perception_service import (
    PerceptionService,
    ALLOWED_AUDIO_EXTENSIONS,
    MAX_FILE_SIZE_BYTES
)

router = APIRouter(prefix="/api/v1/perception", tags=["AI Perception Layer"])

# Global Perception Service Instance
_perception_service = PerceptionService()

def get_perception_service() -> PerceptionService:
    global _perception_service
    if not _perception_service.models_loaded:
        _perception_service.load_models()
    return _perception_service


@router.post(
    "/analyze",
    response_model=PerceptionOutputContract,
    status_code=status.HTTP_200_OK,
    summary="Analyze Multimodal Perception Signals (Audio & Text)",
    description="Extracts STT transcript, acoustic speech features, Wav2Vec2 SER emotions, text distress flags, and composite SVI score."
)
async def analyze_perception(
    request: Request,
    audio: Optional[UploadFile] = File(None, description="Optional uploaded audio file (wav, mp3, m4a, ogg, flac)"),
    text: Optional[str] = Form(None, description="Optional citizen text / transcript string"),
    language: str = Form("hi", description="ISO language code ('hi', 'en', 'ta')"),
    case_id: Optional[str] = Form(None, description="Optional Central Case API Case ID"),
    channel: str = Form("ivrs", description="Ingestion channel ('ivrs', 'phone', 'chat', 'portal', 'mobile_app')")
) -> PerceptionOutputContract:
    """
    Main Perception Endpoint combining STT, Acoustic Analysis, SER, Text Distress, and SVI Fusion.
    """
    service = get_perception_service()

    audio_bytes = None
    filename = None

    # 1. Validate Audio Upload if provided
    if audio is not None:
        filename = audio.filename
        ext = Path(filename).suffix.lower() if filename else ".wav"
        
        if ext not in ALLOWED_AUDIO_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported audio format '{ext}'. Allowed formats: {sorted(list(ALLOWED_AUDIO_EXTENSIONS))}"
            )

        audio_bytes = await audio.read()
        if len(audio_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded audio file is empty (0 bytes)."
            )

        if len(audio_bytes) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Audio file size ({len(audio_bytes)/(1024*1024):.1f}MB) exceeds maximum limit of 50MB."
            )

    # 2. Check Input Requirements (At least one of audio or text must be present)
    has_audio = audio_bytes is not None and len(audio_bytes) > 0
    has_text = text is not None and len(text.strip()) > 0

    if not has_audio and not has_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request payload: Must provide at least one of 'audio' file upload or 'text' payload."
        )

    # 3. Execute Perception Pipeline (Non-blocking via asyncio.to_thread)
    try:
        import asyncio
        contract_payload = await asyncio.to_thread(
            service.analyze,
            audio_bytes=audio_bytes,
            filename=filename,
            text=text,
            language=language,
            case_id=case_id,
            channel=channel
        )
        return contract_payload

    except ValueError as ve:
        print(f"[422 DEBUG] ValueError in analyze_perception: {ve}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        print(f"[API ERROR] Exception during perception pipeline execution: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Perception pipeline error: {str(e)}")


@router.get(
    "/models",
    summary="Get Pre-loaded Perception Models Status",
    description="Returns status of loaded models, hardware acceleration (CUDA/CPU), and VRAM allocation."
)
async def get_models_status():
    service = get_perception_service()
    return service.get_model_status()
