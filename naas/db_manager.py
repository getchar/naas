# -*- coding: utf-8 -*-

import logging
import random
from typing import Callable, List, Optional

from .word_entry import WordEntry
from .check_response import CheckResponse

logger = logging.getLogger(__name__)

FetchCallback = Callable[[str, List[str]], List[WordEntry]]  # (language, known_words) -> words


class DbManager:
    """
    In-memory store of WordEntry objects.
    Guarantees at least `min_num_words` ACTIVE words with
    fewer than `min_num_correct_tries` correct tries in a row.
    """

    def __init__(self, backend: Optional[List[WordEntry]] = None):
        self.backend: List[WordEntry] = backend or []
        self.min_num_words: int = 10
        self.min_num_correct_tries: int = 3

    # -------- helpers --------
    def known_words(self, language: str) -> List[str]:
        return [w.text for w in self.backend if w.language.lower() == language.lower()]

    def unlearned_active_words(self, language: str) -> List[WordEntry]:
        lang = language.lower()
        return [
            w for w in self.backend
            if w.language.lower() == lang and w.active and w.num_correct_tries < self.min_num_correct_tries
        ]

    def inactive_words(self, language: str) -> List[WordEntry]:
        lang = language.lower()
        return [w for w in self.backend if w.language.lower() == lang and not w.active]

    # -------- mutation --------
    def add_words(self, words: List[WordEntry]) -> None:
        """Add as INACTIVE; skip duplicates by (language, text)."""
        existing = {(w.language.lower(), w.text) for w in self.backend}
        added = 0
        for w in words:
            w.active = False
            key = (w.language.lower(), w.text)
            if key in existing:
                continue
            self.backend.append(w)
            existing.add(key)
            added += 1
        logger.debug("Added %d new words", added)

    def score_word(self, original: str, checked_response: CheckResponse) -> None:
        matches = [w for w in self.backend if w.text == original]
        if not matches:
            logger.warning("Tried to score word not in backend: %s", original)
            return
        for w in matches:
            if checked_response.right:
                w.num_correct_tries += 1
            else:
                w.num_correct_tries = 0
        logger.debug("Scored %s; now %s", original, [(w.text, w.num_correct_tries) for w in matches])

    # -------- pool maintenance --------
    def ensure_active_pool(self, language: str, fetch_callback: Optional[FetchCallback] = None) -> None:
        """
        Ensure there are always at least `min_num_words` active & unlearned words.
        1) Activate from inactive.
        2) If still short, fetch with callback(language, known_words) and add, then activate.
        """
        def need() -> int:
            return max(0, self.min_num_words - len(self.unlearned_active_words(language)))

        # Activate from inactive first
        while need() > 0:
            inact = self.inactive_words(language)
            if inact:
                inact[0].active = True
                logger.debug("Activated word: %s", inact[0].text)
                continue

            # Fetch if we have no inactive to promote
            if not fetch_callback:
                raise ValueError(f"Not enough words for {language} and no fetch_callback provided.")

            new_words = fetch_callback(language, self.known_words(language))
            if not new_words:
                raise ValueError(f"fetch_callback returned no words for {language}.")
            self.add_words(new_words)

    def get_word(self, language: str, fetch_callback: Optional[FetchCallback] = None) -> WordEntry:
        self.ensure_active_pool(language, fetch_callback)
        pool = self.unlearned_active_words(language)
        if not pool:
            raise ValueError(f"No active unlearned words available for '{language}'.")
        return random.choice(pool)

    # -------- dumps --------
    def all_words(self, language: str) -> List[str]:
        return [w.text for w in self.backend if w.language.lower() == language.lower()]

    def dump_word_entries(self, language: str) -> str:
        rows = [
            f"{w.language}: {w.text} | active={w.active} | tries={w.num_correct_tries}"
            for w in self.backend if w.language.lower() == language.lower()
        ]
        return "\n".join(rows)
