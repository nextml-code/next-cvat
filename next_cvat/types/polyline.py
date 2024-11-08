from __future__ import annotations

from typing import List, Tuple

from pydantic import BaseModel, field_validator

from .attribute import Attribute


class Polyline(BaseModel):
    label: str
    source: str
    occluded: int
    points: List[Tuple[float, float]]
    z_order: int
    attributes: List[Attribute]

    @field_validator("points", mode="before")
    def parse_points(cls, v):
        if isinstance(v, str):
            return [tuple(map(float, point.split(","))) for point in v.split(";")]
        else:
            return v

    def leftmost(self) -> float:
        return min([x for x, _ in self.points])

    def rightmost(self) -> float:
        return max([x for x, _ in self.points])

    def topmost(self) -> float:
        return min([y for _, y in self.points])

    def bottommost(self) -> float:
        return max([y for _, y in self.points])
