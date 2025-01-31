from __future__ import annotations

from typing import List

from pydantic import BaseModel

from .attribute import Attribute


class Ellipse(BaseModel):
    """Ellipse annotation in CVAT.

    Represents an ellipse shape annotation with center point (cx, cy) and radii (rx, ry).

    Attributes:
        label: Label name for the ellipse
        source: Source of the annotation (e.g., "manual")
        occluded: Whether the ellipse is occluded
        cx: X-coordinate of ellipse center
        cy: Y-coordinate of ellipse center
        rx: Radius in X direction
        ry: Radius in Y direction
        z_order: Z-order of the ellipse (drawing order)
        attributes: List of attributes associated with the ellipse

    Example:
        ```python
        ellipse = Ellipse(
            label="Deformation",
            source="manual",
            occluded=0,
            cx=3126.92,
            cy=509.86,
            rx=39.99,
            ry=18.92,
            z_order=0,
            attributes=[
                Attribute(name="Damage Level", value="0")
            ]
        )
        ```
    """

    label: str
    source: str = "manual"
    occluded: int = 0
    cx: float
    cy: float
    rx: float
    ry: float
    z_order: int = 0
    attributes: List[Attribute] = []
