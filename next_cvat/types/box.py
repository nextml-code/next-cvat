from __future__ import annotations

from typing import List, Optional

import numpy as np
from pydantic import BaseModel

from .attribute import Attribute
from .polygon import Polygon


class Box(BaseModel):
    """A bounding box annotation in CVAT.

    Represents a rectangular region in an image with a label and optional attributes.
    Coordinates are specified in pixels from the top-left corner of the image.

    Attributes:
        label: Name of the label assigned to this box
        xtl: X-coordinate of top-left corner
        ytl: Y-coordinate of top-left corner
        xbr: X-coordinate of bottom-right corner
        ybr: Y-coordinate of bottom-right corner
        occluded: Whether the object is occluded
        z_order: Drawing order (higher numbers are drawn on top)
        attributes: List of additional attributes for this box

    Example:
        ```python
        # Simple box
        box = Box(
            label="car",
            xtl=100,
            ytl=200,
            xbr=300,
            ybr=400,
            occluded=False,
            z_order=1
        )

        # Box with attributes
        box_with_attrs = Box(
            label="car",
            xtl=100,
            ytl=200,
            xbr=300,
            ybr=400,
            attributes=[
                Attribute(name="color", value="red"),
                Attribute(name="model", value="sedan")
            ]
        )
        ```
    """

    label: str
    xtl: float
    ytl: float
    xbr: float
    ybr: float
    occluded: bool = False
    z_order: int = 0
    attributes: List[Attribute] = []

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

    def segmentation(self, height: int, width: int) -> np.ndarray:
        return self.polygon().segmentation(height, width)
