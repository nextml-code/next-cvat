from __future__ import annotations

from typing import List

from pydantic import BaseModel

from .attribute import Attribute
from .polygon import Polygon


class Box(BaseModel):
    label: str
    source: str
    occluded: int
    xtl: float
    ytl: float
    xbr: float
    ybr: float
    z_order: int
    attributes: List[Attribute]

    def polygon(self) -> Polygon:
        points = [
            (self.xtl, self.ytl),
            (self.xbr, self.ytl),
            (self.xbr, self.ybr),
            (self.xtl, self.ybr),
        ]
        return Polygon(
            label=self.label,
            source=self.source,
            occluded=self.occluded,
            points=points,
            z_order=self.z_order,
            attributes=self.attributes,
        )
