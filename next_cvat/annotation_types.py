from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw
from pydantic import BaseModel, field_validator


class Task(BaseModel):
    task_id: str
    url: str

    def job_id(self) -> str:
        """
        Extracts the job ID from the given URL.
        Assumes the job ID is the last numeric part of the URL.
        """
        parts = self.url.rstrip("/").split("/")
        for part in reversed(parts):
            if part.isdigit():
                return part
        raise ValueError(f"Could not extract job ID from URL: {self.url}")


class LabelAttribute(BaseModel):
    name: str
    mutable: Optional[str] = None
    input_type: Optional[str] = None
    default_value: Optional[str] = None
    values: Optional[str] = None


class Label(BaseModel):
    name: str
    color: str
    type: str
    attributes: List[LabelAttribute]


class Project(BaseModel):
    id: str
    name: str
    created: str
    updated: str
    labels: List[Label]


class Attribute(BaseModel):
    name: str
    value: str


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


class Mask(BaseModel):
    label: str
    source: str
    occluded: int
    z_order: int
    rle: str
    top: int
    left: int
    height: int
    width: int
    attributes: List[Attribute]

    def segmentation(self, height: int, width: int) -> np.ndarray:
        """
        Create a boolean segmentation mask for the polygon.

        :param height: Height of the output mask.
        :param width: Width of the output mask.
        :return: A numpy 2D array of booleans.
        """
        small_mask = self.rle_decode()
        mask = np.zeros((height, width), dtype=bool)
        mask[self.top : self.top + self.height, self.left : self.left + self.width] = (
            small_mask
        )
        return mask

    def rle_decode(self):
        s = self.rle.split(",")
        mask = np.empty((self.height * self.width), dtype=bool)
        index = 0
        for i in range(len(s)):
            if i % 2 == 0:
                mask[index : index + int(s[i])] = False
            else:
                mask[index : index + int(s[i])] = True
            index += int(s[i])
        return np.array(mask, dtype=bool).reshape(self.height, self.width)


class Polyline(BaseModel):
    label: str
    source: str
    occluded: int
    points: List[Tuple[float, float]]
    z_order: int

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


class Annotations(BaseModel):
    version: str
    project: Project
    tasks: List[Task]
    images: List[ImageAnnotation]

    def create_cvat_link(self, image_name: str) -> str:
        """
        Create a CVAT link for the given image name.

        :param image_name: Name of the image.
        :return: A CVAT link. E.g. https://app.cvat.ai/tasks/453747/jobs/520016
        """
        # lookup task id for the given image name
        task_id = None
        for image in self.images:
            if Path(image.name).name == image_name:
                task_id = image.task_id
                image_id = image.id
                break
        if task_id is None:
            raise ValueError(f"Could not find task ID for image: {image_name}")

        frame_index = 0
        for image in self.images:
            if image.task_id == task_id:
                if Path(image.name).name == image_name:
                    break

                frame_index += 1

        # lookup job id for the given task id
        job_id = None
        for task in self.tasks:
            if task.task_id == task_id:
                job_id = task.job_id()
                break
        if job_id is None:
            raise ValueError(f"Could not find job ID for task ID: {task_id}")

        return f"https://app.cvat.ai/tasks/{task_id}/jobs/{job_id}?frame={frame_index}"
