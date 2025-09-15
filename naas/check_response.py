# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing import List, Optional

class ScratchItem(BaseModel):
    letter: str
    mapped: str

class CheckResponse(BaseModel):
    right: bool
    message: str
    correct_transliteration: str
    scratch: List[ScratchItem]
    message_transliteration: Optional[str] = None
    message_translation: Optional[str] = None
