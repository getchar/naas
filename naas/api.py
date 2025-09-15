# -*- coding: utf-8 -*-

import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from .db_manager import DbManager
from .llm_manager import LlmManager
from .service import Service
from .word_entry import WordEntry
from .check_response import CheckResponse

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)
app = FastAPI(title="Naas API", version="1.0.0")

try:
    db_manager = DbManager([])
    llm_manager = LlmManager()
    service = Service(db_manager, llm_manager)
except Exception:
    logger.exception("Failed to initialize service dependencies")
    raise

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/dump/{language}", response_class=PlainTextResponse)
def dump_word_entries(language: str):
    try:
        return service.dump_word_entries(language)
    except Exception as e:
        logger.exception("Failed to dump word entries for %s", language)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/word/{language}", response_model=WordEntry)
def get_word(language: str):
    try:
        return service.get_word(language)
    except Exception as e:
        logger.exception("Failed to fetch word for %s", language)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/check/{language}/{original}/{transliteration}", response_model=CheckResponse)
def check_word(language: str, original: str, transliteration: str):
    try:
        return service.check_word(language, original, transliteration)
    except Exception as e:
        logger.exception("Unable to check transliteration for %s / %s / %s",
                         language, original, transliteration)
        raise HTTPException(status_code=500, detail=str(e))
