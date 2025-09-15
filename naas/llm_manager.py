# -*- coding: utf-8 -*-

from typing import List
from pathlib import Path
import logging
import os
import json
import runpy

from jinja2 import Template
import yaml
from openai import OpenAI

from .word_entry import WordEntry
from .check_response import CheckResponse

logger = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent


def load_prompt(filename: str, **vars):
    path = HERE / "prompts" / f"{filename}.yaml"
    text = path.read_text(encoding="utf-8")
    rendered = Template(text).render(**vars)
    logger.debug("Loaded prompt %s:\n%s", filename, rendered)
    try:
        return yaml.safe_load(rendered)
    except Exception:
        logger.exception("Failed to parse rendered YAML for %s", filename)
        raise


def load_scheme(language: str) -> str:
    """
    Load global `scheme` from schemes/{language}.py using runpy.
    """
    scheme_path = HERE.parent / "schemes" / f"{language}.py"
    if not scheme_path.is_file():
        raise FileNotFoundError(
            f"Scheme file not found: {scheme_path}. "
            f"Expected a file named '{language}.py' in the 'schemes' directory."
        )
    globs = runpy.run_path(str(scheme_path))
    if "scheme" not in globs:
        raise KeyError(f"The file '{scheme_path}' does not define a variable named 'scheme'.")
    scheme = globs["scheme"]
    logger.debug("Loaded scheme:\n%s", scheme)
    return scheme


class LlmManager:
    def __init__(self, model: str = "gpt-4o"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set. Did you export it?")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    # -------- batches --------
    def get_batch_of_words(self, language: str, known_words: List[str]) -> List[WordEntry]:
        prompt = load_prompt("word_batch", language=language,
                             known_words=known_words, number=10)
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=prompt.get("temperature", 0),
            response_format=prompt.get("response_format", {"type": "json_object"}),
            messages=prompt["messages"]
        )
        content = resp.choices[0].message.content
        logger.debug("Raw model output: %r", resp)
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from model output: %s", content)
            raise
        words = [WordEntry(**item) for item in parsed.get("words", [])]
        logger.debug("LLM returned words: %s", [w.text for w in words])
        return words

    # -------- check word --------
    def check_word(self, language: str, original: str, transliteration: str) -> CheckResponse:
        scheme_str = load_scheme(language)
        check_prompt = load_prompt(
            "check_transliteration",
            language=language,
            original=original,
            transliteration=transliteration,
            transliteration_scheme=scheme_str,
        )
        check_output = self.client.chat.completions.create(
            model=self.model,
            temperature=check_prompt.get("temperature", 0),
            response_format=check_prompt.get("response_format", {"type": "json_object"}),
            messages=check_prompt["messages"]
        )
        checked = CheckResponse(**json.loads(check_output.choices[0].message.content))

        # Friendly response prompt (optional flavor)
        nana_prompt = load_prompt(
            "nan_it_up",
            language=language,
            word=original,
            attempt=transliteration,
            right=checked.right,
            correct_transliteration=checked.correct_transliteration
        )
        nana_output = self.client.chat.completions.create(
            model=self.model,
            temperature=nana_prompt.get("temperature", 0),
            response_format=nana_prompt.get("response_format", {"type": "json_object"}),
            messages=nana_prompt["messages"]
        )
        extra = json.loads(nana_output.choices[0].message.content)
        logger.debug(extra)
        checked.message = extra.get("message", checked.message)
        checked.message_transliteration = extra.get("transliteration")
        checked.message_translation = extra.get("gloss")
        return checked
