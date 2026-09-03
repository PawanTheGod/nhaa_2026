"""
Deepgram live STT client for Twilio media streams.

Twilio sends audio as base64-encoded mulaw/8kHz over a WebSocket.
This client connects to Deepgram's streaming API, forwards the audio,
and yields interim + final transcripts back to the call orchestrator.

Uses Deepgram's free tier (200 hours/month) with the Nova-2 model.
Supports Hindi (hi), English (en), and 30+ other languages.
"""
from __future__ import annotations

import os
import json
import base64
import logging
import asyncio
from typing import AsyncIterator, Optional

import websockets
import httpx

log = logging.getLogger("nhaa.stt")

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
DEEPGRAM_URL = "wss://api.deepgram.com/v1/listen"


class DeepgramStream:
    """
    Live transcription session.

    Usage:
        dg = DeepgramStream(language="hi")
        await dg.start()
        await dg.send_audio(audio_bytes)
        async for transcript, is_final in dg.results():
            if is_final:
                ...
        await dg.close()
    """

    def __init__(self, language: str = "hi", sample_rate: int = 8000, encoding: str = "mulaw"):
        self.api_key = DEEPGRAM_API_KEY
        self.language = language
        self.sample_rate = sample_rate
        self.encoding = encoding
        self._ws = None
        self._results: asyncio.Queue = asyncio.Queue()
        self._closed = False

    async def start(self) -> None:
        if not self.api_key:
            raise RuntimeError("DEEPGRAM_API_KEY not set in env")
        params = (
            f"language={self.language}"
            f"&sample_rate={self.sample_rate}"
            f"&encoding={self.encoding}"
            f"&model=nova-2"
            f"&interim_results=true"
            f"&endpointing=300"
            f"&vad_events=true"
        )
        url = f"{DEEPGRAM_URL}?{params}"
        log.info("DeepgramStream connecting: %s", url)
        self._ws = await websockets.connect(
            url,
            extra_headers={"Authorization": f"Token {self.api_key}"},
            ping_interval=20,
        )
        asyncio.create_task(self._reader())

    async def _reader(self) -> None:
        try:
            async for raw in self._ws:
                if self._closed:
                    return
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if msg.get("type") == "Results":
                    channel = msg.get("channel", {})
                    alts = channel.get("alternatives", [])
                    if not alts:
                        continue
                    best = alts[0]
                    transcript = best.get("transcript", "")
                    is_final = bool(msg.get("is_final"))
                    if transcript.strip():
                        await self._results.put((transcript, is_final))
                elif msg.get("type") == "UtteranceEnd":
                    await self._results.put(("", True))
        except websockets.ConnectionClosed as e:
            log.info("Deepgram stream closed: %s", e)
        except Exception as e:
            log.exception("Deepgram reader error: %s", e)

    async def send_audio(self, audio_bytes: bytes) -> None:
        """Send raw audio bytes (mulaw/8kHz from Twilio) to Deepgram."""
        if self._closed or self._ws is None:
            return
        try:
            await self._ws.send(audio_bytes)
        except websockets.ConnectionClosed:
            self._closed = True
        except Exception as e:
            log.warning("send_audio failed: %s", e)

    async def results(self, timeout: float = 0.5) -> AsyncIterator[tuple[str, bool]]:
        """Yield (transcript, is_final) tuples as they arrive."""
        while not self._closed:
            try:
                item = await asyncio.wait_for(self._results.get(), timeout=timeout)
                yield item
            except asyncio.TimeoutError:
                if self._closed:
                    return
                continue

    async def close(self) -> None:
        self._closed = True
        if self._ws is not None:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None
        log.info("DeepgramStream closed")


# ─── Standalone one-shot transcription (for browser demo uploads) ────────────
async def transcribe_bytes(audio_bytes: bytes, *, language: str = "hi", mimetype: str = "audio/wav") -> str:
    """
    Transcribe a complete audio blob (file upload from browser demo) via Deepgram's REST API.
    Returns the best transcript.
    """
    if not DEEPGRAM_API_KEY:
        raise RuntimeError("DEEPGRAM_API_KEY not set in env")
    url = (
        f"https://api.deepgram.com/v1/listen"
        f"?language={language}&model=nova-2&smart_format=true"
    )
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": mimetype,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url, headers=headers, content=audio_bytes)
        r.raise_for_status()
        data = r.json()
        return data.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
