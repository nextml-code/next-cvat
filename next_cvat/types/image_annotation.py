from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from .box import Box
from .mask import Mask
from .polygon import Polygon
from .polyline import Polyline


class ImageAnnotation(BaseModel):
    """Annotation data for a single image in CVAT.

    Contains all annotation shapes (boxes, polygons, masks, polylines) associated with an image.

    Attributes:
        id: Unique identifier for the image
        name: Filename of the image
        subset: Optional subset the image belongs to (e.g., "train", "test")
        task_id: ID of the task this image belongs to
        width: Image width in pixels
        height: Image height in pixels
        boxes: List of bounding box annotations
        polygons: List of polygon annotations
        masks: List of mask annotations
        polylines: List of polyline annotations

    Example:
        ```python
        image = ImageAnnotation(
            id="1",
            name="frame_000001.jpg",
            subset="train",
            task_id="906591",
            width=1920,
            height=1080,
            boxes=[
                Box(label="car", xtl=100, ytl=200, xbr=300, ybr=400)
            ],
            masks=[
                Mask(label="person", points="100,200;300,400", z_order=1)
            ]
        )
        ```
    """

    id: str
    name: str
    subset: Optional[str] = None
    task_id: Optional[str] = None
    width: int
    height: int
    boxes: List[Box] = []
    polygons: List[Polygon] = []
    masks: List[Mask] = []
    polylines: List[Polyline] = []