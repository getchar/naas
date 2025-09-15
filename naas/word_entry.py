# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import List, Optional

class WordEntry(BaseModel):
    text: str
    language: str
    definition: Optional[str] = None
    etymology: Optional[str] = None
    cognates: Optional[List[str]] = None
    num_correct_tries: int = 0
    active: bool = False
