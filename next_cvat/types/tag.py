from __future__ import annotations

from typing import List

from pydantic import BaseModel

from .attribute import Attribute


class Tag(BaseModel):
    label: str
    source: str
    attributes: List[Attribute]
