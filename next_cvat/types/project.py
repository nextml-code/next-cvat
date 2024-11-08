from __future__ import annotations

from typing import List

from pydantic import BaseModel

from .label import Label


class Project(BaseModel):
    id: str
    name: str
    created: str
    updated: str
    labels: List[Label]
