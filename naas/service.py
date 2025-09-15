# -*- coding: utf-8 -*-

import logging
from typing import List

from .db_manager import DbManager
from .llm_manager import LlmManager
from .word_entry import WordEntry
from .check_response import CheckResponse

logger = logging.getLogger(__name__)


class Service:
    def __init__(self, db: DbManager, llm: LlmManager):
        self.db = db
        self.llm = llm

    def fetch_from_llm(self, language: str, known: List[str]) -> List[WordEntry]:
        return self.llm.get_batch_of_words(language, known_words=known)

    def get_word(self, language: str) -> WordEntry:
        return self.db.get_word(language, fetch_callback=self.fetch_from_llm)

    def dump_word_entries(self, language: str) -> str:
        return self.db.dump_word_entries(language)

    def check_word(self, language: str, original: str, transliteration: str) -> CheckResponse:
        resp = self.llm.check_word(language, original, transliteration)
        # score after check
        try:
            self.db.score_word(original, resp)
        except Exception:
            logger.exception("Failed to update score for %s", original)
        return resp
