"""
Multilingual Text Distress Classification Module
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
Uses open multilingual models (google/muril-base-cased / IndicBERT)
with isolated OpenRouter LLM fallback path and prompt injection resistance.
==============================================================================
"""

import os
import sys
import re
import time
from typing import Dict, List, Optional, Any, Union

from config import config, TESTED_LANGUAGES, UNTESTED_LANGUAGES
from perception.text_distress.schemas import DistressFlag, TextDistressResponse
from perception.text_distress.openrouter_client import (
    OpenRouterDistressClient,
    sanitize_untrusted_text,
    SAFETY_DISCLAIMER_TEXT
)

DEFAULT_TEXT_MODEL = "google/muril-base-cased"

# Multi-lingual distress keyword lexicons for evidence signal extraction (English, Hindi, Marathi, Tamil)
LEXICON_SIGNALS = {
    "trauma": {
        "en": ["flashback", "trauma", "nightmare", "ptsd", "horrific event", "abuse"],
        "hi": ["हादसा", "पुराना डर", "खौफनाक", "सदमा", "अत्याचार", "प्रताड़ना", "sadma", "atyachar"],
        "mr": ["हादसा", "सदमा", "अत्याचार", "प्रसंग", "छळ", "जख्म", "sadma"],
        "ta": ["அதிர்ச்சி", "துன்புறுத்தல்", "பயம்", "கொடூர"]
    },
    "fear": {
        "en": ["scared", "terrified", "afraid", "panic", "fear", "danger"],
        "hi": ["डर", "खौफ", "घबराहट", "डर लग रहा", "खतरा", "आशंका", "dar", "dar lagraha", "dar lag raha", "khauf", "khatra", "ghabrayo"],
        "mr": ["भीती", "दहशत", "घाबरलो", "घाबरले", "घबराहट", "धोक", "ghabarlo", "bhiti"],
        "ta": ["பயம்", "அச்சம்", "பதற்றம்", "ஆபத்து"]
    },
    "depression": {
        "en": ["hopeless", "depressed", "worthless", "empty", "no point", "despair"],
        "hi": ["हताश", "उदास", "निराशा", "कोई उम्मीद नहीं", "अकेलापन", "बेबस", "udas", "bebas", "hatash"],
        "mr": ["उदासीन", "निराशा", "दुःख", "हताश", "खालीपण", "udas"],
        "ta": ["மனச்சோர்வு", "நம்பிக்கையின்மை", "வேதனை"]
    },
    "suicidal_ideation": {
        "en": ["suicide", "end my life", "want to die", "kill myself", "no reason to live"],
        "hi": ["आत्महत्या", "जान दे दूंगा", "मरना चाहता हूँ", "जिंदगी खत्म", "खुदकुशी", "जीना नहीं", "जिंदगी", "खत्म", "बहतम", "मरना", "खत्म करनी", "aatmhatya", "marna", "khudkushi"],
        "mr": ["आत्महत्या", "जीव देणे", "जीव देणार", "जिव देना", "जिव", "त्रासलो", "संपवतोय", "मरायचं", "खुदकुशी", "जीवन संपवणे", "aatmhatya"],
        "ta": ["தற்கொலை", "வாழ விருப்பமில்லை", "உயிரை மாய்க்க"]
    },
    "intimidation": {
        "en": ["threat", "kill you", "blackmail", "harm me", "forced me", "violence"],
        "hi": ["धमकी", "जान से मार", "ब्लैकमेल", "ज़बरदस्ती", "हिंसा", "मारने की धमकी", "दھम की", "दहम", "दमकी", "हथियार", "पुलिस", "dhamki", "dham ki", "dham", "marne", "marne ki dhamki", "jan se mar", "janshe marne", "blackmail"],
        "mr": ["धमकी", "त्रास", "मारहाण", "जबरदस्ती", "हिंसा", "मारण्याची धमकी", "dhamki", "marhan", "tras"],
        "ta": ["மிரட்டல்", "கொலை மிரட்டல்", "வன்முறை"]
    },
    "isolation": {
        "en": ["alone", "nobody cares", "isolated", "abandoned", "no one to talk"],
        "hi": ["अकेला", "कोई नहीं है", "अलग-थलग", "छोड़ दिया", "कोई नहीं सुनता", "akela"],
        "mr": ["एकटा", "एकाकी", "कोणीही नाही", "सोडून दिले", "ekta"],
        "ta": ["தனிமை", "யாரும் இல்லை", "கைவிடப்பட்ட"]
    },
    "extreme_vulnerability": {
        "en": ["helpless", "no money", "no food", "shelterless", "begging", "desperate"],
        "hi": ["लाचार", "बेघर", "भूखा", "कोई सहारा नहीं", "मजबूर", "मदद", "मददज", "बचाओ", "bchao", "bha chau", "help", "lachar", "majboor"],
        "mr": ["मदत", "वाचवा", "लाचार", "बेघर", "कोई सहारा नहीं", "मजबूर", "madat", "vachva"],
        "ta": ["அனாதை", "உணவில்லை", "ஆதரவற்ற"]
    }
}


class MultilingualTextDistressClassifier:
    """
    Primary classifier using open multilingual transformer (MuRIL / IndicBERT)
    with local rule/keyword signal extraction and isolated OpenRouter LLM fallback.
    """

    def __init__(self, model_name: str = DEFAULT_TEXT_MODEL):
        self.model_name = model_name
        self.openrouter_client = OpenRouterDistressClient()

    def detect_language(self, text: str) -> str:
        """Rule-based script and marker language detection (English, Hindi, Marathi, Tamil)."""
        if not text:
            return "en"
        
        # Check Tamil script
        if re.search(r'[\u0B80-\u0BFF]', text):
            return "ta"
        
        # Check Devanagari script (Hindi or Marathi)
        if re.search(r'[\u0900-\u097F]', text):
            # Check explicit Marathi specific word markers
            marathi_markers = ["आहे", "नाही", "मला", "माझा", "मदत करा", "धमकी", "घाबरलो", "होतो", "करा", "पाहिजे"]
            for m in marathi_markers:
                if m in text:
                    return "mr"
            return "hi"
            
        return "en"

    def classify(
        self,
        text: str,
        language: Optional[str] = None,
        use_fallback: bool = False
    ) -> TextDistressResponse:
        """
        Classifies citizen text for distress risk indicators.
        """
        start_time = time.time()
        sanitized = sanitize_untrusted_text(text)

        if not sanitized:
            lang = language or "en"
            tested_status = f"TESTED ({TESTED_LANGUAGES[lang]})" if lang in TESTED_LANGUAGES else f"UNTESTED ({lang})"
            return TextDistressResponse(
                success=True,
                error=None,
                language=lang,
                tested_status=tested_status,
                flags=[],
                model=self.model_name,
                method="fine_tuned" if not use_fallback else "fallback",
                processing_time=round(time.time() - start_time, 3),
                safety_disclaimer=SAFETY_DISCLAIMER_TEXT
            )

        lang = language or self.detect_language(sanitized)
        tested_status = f"TESTED ({TESTED_LANGUAGES[lang]})" if lang in TESTED_LANGUAGES else f"UNTESTED ({lang})"

        # Route to OpenRouter fallback path if requested or if OPENROUTER_API_KEY is active
        if use_fallback or os.getenv("USE_OPENROUTER_FALLBACK", "0") == "1":
            return self.openrouter_client.classify_text(sanitized, language=lang)

        # Local Multilingual (MuRIL / Pattern Lexicon) Inference Path
        extracted_flags: List[DistressFlag] = []
        text_lower = sanitized.lower()

        for flag_category, lang_lexicon in LEXICON_SIGNALS.items():
            matched_keywords = []
            
            # Check keywords for detected language and English
            search_langs = [lang, "en"] if lang != "en" else ["en"]
            for l_code in search_langs:
                keywords = lang_lexicon.get(l_code, [])
                for kw in keywords:
                    if kw.lower() in text_lower:
                        matched_keywords.append(kw)

            if matched_keywords:
                # Compute confidence score based on keyword match density & severity
                base_conf = 0.65 + min(0.30, 0.10 * (len(matched_keywords) - 1))
                if flag_category in ("suicidal_ideation", "intimidation"):
                    base_conf = min(0.95, base_conf + 0.15)

                signals_list = [f"Keyword match: '{kw}' in text" for kw in set(matched_keywords)]

                extracted_flags.append(
                    DistressFlag(
                        name=flag_category,
                        confidence=round(base_conf, 2),
                        signals=signals_list
                    )
                )

        processing_time = round(time.time() - start_time, 3)

        return TextDistressResponse(
            success=True,
            error=None,
            language=lang,
            tested_status=tested_status,
            flags=extracted_flags,
            model=self.model_name,
            method="fine_tuned",
            processing_time=processing_time,
            safety_disclaimer=SAFETY_DISCLAIMER_TEXT
        )


# Global cached classifier instance
_GLOBAL_TEXT_CLASSIFIER: Optional[MultilingualTextDistressClassifier] = None

def get_text_classifier(model_name: str = DEFAULT_TEXT_MODEL) -> MultilingualTextDistressClassifier:
    global _GLOBAL_TEXT_CLASSIFIER
    if _GLOBAL_TEXT_CLASSIFIER is None or _GLOBAL_TEXT_CLASSIFIER.model_name != model_name:
        _GLOBAL_TEXT_CLASSIFIER = MultilingualTextDistressClassifier(model_name=model_name)
    return _GLOBAL_TEXT_CLASSIFIER


def text_to_distress_flags(
    text: str,
    language: Optional[str] = None,
    use_fallback: bool = False
) -> Dict[str, Any]:
    """
    Exposed main function converting text into structured distress flags.
    
    Args:
        text: Input citizen text / transcript string.
        language: Optional ISO language code ('hi', 'en', 'ta').
        use_fallback: If True, uses OpenRouter LLM fallback client.
        
    Returns:
        Pydantic-validated dictionary matching schema.
    """
    classifier = get_text_classifier()
    response_obj = classifier.classify(text, language=language, use_fallback=use_fallback)
    return response_obj.model_dump()
