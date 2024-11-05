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

    def rle_encode(self, mask: np.ndarray) -> str:
        """
        Encode a binary mask into an RLE string.

        :param mask: A numpy 2D array of booleans.
        :return: RLE string.
        """
        # Flatten the mask in row-major order
        flat_mask = mask.flatten(order="C")
        # Initialize the counts list
        counts = []
        # Initialize the previous pixel value and count
        prev_pixel = flat_mask[0]
        count = 1

        # Iterate over the flattened mask starting from the second pixel
        for pixel in flat_mask[1:]:
            if pixel == prev_pixel:
                count += 1
            else:
                counts.append(count)
                count = 1
                prev_pixel = pixel
        counts.append(count)

        # Ensure the RLE starts with the count of zeros (False pixels)
        if flat_mask[0]:
            counts = [0] + counts

        # Convert counts to a comma-separated string
        rle_string = ",".join(map(str, counts))
        return rle_string


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


def test_rle_encode_decode():
    """
    Test that encoding a mask and then decoding it returns the original mask.
    """
    import numpy as np

    # Create a random binary mask
    height, width = 10, 10
    original_mask = np.random.choice([False, True], size=(height, width))

    # Create a Mask instance
    mask_instance = Mask(
        label="test",
        source="test",
        occluded=0,
        z_order=0,
        rle="",  # Will set this after encoding
        top=0,
        left=0,
        height=height,
        width=width,
        attributes=[],
    )

    # Encode the original mask
    mask_instance.rle = mask_instance.rle_encode(original_mask)

    # Decode the RLE string back to a mask
    decoded_mask = mask_instance.rle_decode()

    # Verify that the original and decoded masks are the same
    assert np.array_equal(
        original_mask, decoded_mask
    ), "The decoded mask does not match the original mask."


def test_rle_decode_encode():
    """
    Test that decoding an RLE string and then encoding the mask returns the original RLE string.
    """
    import numpy as np

    # Corrected RLE string with counts summing to 15 (total pixels)
    original_rle = "0,3,2,5,4,1"
    height = 5
    width = 3  # Total pixels = 15

    # Create a Mask instance with the original RLE
    mask_instance = Mask(
        label="test",
        source="test",
        occluded=0,
        z_order=0,
        rle=original_rle,
        top=0,
        left=0,
        height=height,
        width=width,
        attributes=[],
    )

    # Decode the RLE string to get the mask
    decoded_mask = mask_instance.rle_decode()

    # Encode the mask back into an RLE string
    encoded_rle = mask_instance.rle_encode(decoded_mask)

    # Verify that the original and encoded RLE strings are the same
    assert original_rle == encoded_rle, (
        f"The encoded RLE does not match the original RLE.\n"
        f"Original RLE: {original_rle}\n"
        f"Encoded RLE: {encoded_rle}"
    )


def generate_random_rle(height, width):
    import numpy as np

    # Create a random binary mask
    mask = np.random.choice([False, True], size=(height, width))

    # Flatten the mask and encode it into an RLE string
    flat_mask = mask.flatten(order="C")
    counts = []
    prev_pixel = flat_mask[0]
    count = 1

    for pixel in flat_mask[1:]:
        if pixel == prev_pixel:
            count += 1
        else:
            counts.append(count)
            count = 1
            prev_pixel = pixel
    counts.append(count)

    if flat_mask[0]:
        counts = [0] + counts

    rle_string = ",".join(map(str, counts))
    return rle_string, height, width


def test_rle_decode_encode_random():
    """
    Test that decoding and then encoding a random RLE string returns the original RLE string.
    """

    # Generate a random RLE string
    height, width = 10, 10
    original_rle, height, width = generate_random_rle(height, width)

    # Create a Mask instance
    mask_instance = Mask(
        label="test",
        source="test",
        occluded=0,
        z_order=0,
        rle=original_rle,
        top=0,
        left=0,
        height=height,
        width=width,
        attributes=[],
    )

    # Decode and then encode the RLE string
    decoded_mask = mask_instance.rle_decode()
    encoded_rle = mask_instance.rle_encode(decoded_mask)

    # Verify that the original and encoded RLE strings are the same
    assert (
        original_rle == encoded_rle
    ), "The encoded RLE does not match the original RLE."
