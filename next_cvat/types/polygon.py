from __future__ import annotations

from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw
from pydantic import BaseModel, field_validator

from .attribute import Attribute


class Polygon(BaseModel):
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

    def segmentation(self, height: int, width: int) -> np.ndarray:
        """
        Create a boolean segmentation mask for the polygon.

        :param height: Height of the output mask.
        :param width: Width of the output mask.
        :return: A numpy 2D array of booleans.
        """
        mask = Image.new("L", (width, height), 0)
        ImageDraw.Draw(mask).polygon(self.points, outline=1, fill=1)
        return np.array(mask).astype(bool)

    def translate(self, dx: int, dy: int) -> Polygon:
        """
        Translate the polygon by (dx, dy).

        :param dx: Amount to translate in the x direction.
        :param dy: Amount to translate in the y direction.
        :return: A new Polygon.
        """
        return Polygon(
            label=self.label,
            source=self.source,
            occluded=self.occluded,
            points=[(x + dx, y + dy) for x, y in self.points],
            z_order=self.z_order,
            attributes=self.attributes,
        )

    def polygon(self) -> Polygon:
        return self
