from __future__ import annotations

from typing import List

from pydantic import BaseModel

from .box import Box
from .mask import Mask
from .polygon import Polygon
from .polyline import Polyline


class ImageAnnotation(BaseModel):
    id: str
    name: str
    subset: str
    task_id: str
    width: int
    height: int
    boxes: List[Box] = []
    polygons: List[Polygon] = []
    masks: List[Mask] = []
    polylines: List[Polyline] = []
