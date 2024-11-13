from __future__ import annotations

from typing import TYPE_CHECKING

from cvat_sdk.api_client import models
from PIL import Image
from pydantic import BaseModel

if TYPE_CHECKING:
    from .task import Task


class Frame(BaseModel, arbitrary_types_allowed=True):
    task: Task
    id: int
    frame_info: models.IFrameMeta

    @property
    def cvat(self) -> models.IFrameMeta:
        return self.frame_info

    def pil_image(self) -> Image.Image:
        with self.task.cvat() as cvat_task:
            frame_bytes = cvat_task.get_frame(self.id)
            return Image.open(frame_bytes)

    def _repr_png_(self) -> bytes:
        return self.pil_image()._repr_png_()
