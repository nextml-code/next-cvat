from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
from cvat_sdk.api_client import models
from PIL import Image
from pydantic import BaseModel

from .attribute import Attribute


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

    @classmethod
    def from_segmentation(
        cls,
        segmentation: np.ndarray | Image.Image,
        label: str,
        source: str = "next-cvat",
        occluded: int = 0,
        z_order: int = 0,
        attributes: List[Attribute] = [],
    ) -> Mask:
        if isinstance(segmentation, Image.Image):
            segmentation = np.array(segmentation)

        # Handle RGB/RGBA images by taking mean across color channels
        if len(segmentation.shape) == 3:
            segmentation = segmentation.mean(axis=2) > 0
        else:
            segmentation = segmentation > 0

        # Find the bounding box of the segmentation
        rows = np.any(segmentation, axis=1)
        cols = np.any(segmentation, axis=0)

        if not np.any(rows) or not np.any(cols):
            raise ValueError("Cannot create mask from empty segmentation")

        top = np.where(rows)[0][0]
        bottom = np.where(rows)[0][-1] + 1
        left = np.where(cols)[0][0]
        right = np.where(cols)[0][-1] + 1

        height = bottom - top
        width = right - left

        crop = segmentation[top:bottom, left:right]
        rle = cls.rle_encode(crop)

        return cls(
            label=label,
            source=source,
            occluded=occluded,
            z_order=z_order,
            rle=rle,
            top=top,
            left=left,
            height=height,
            width=width,
            attributes=attributes,
        )

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

    @classmethod
    def rle_encode(cls, mask: np.ndarray) -> str:
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

    def request(
        self,
        frame: int,
        label_id: int,
        group: int = 0,
    ) -> models.LabeledShapeRequest:
        """
        Convert the mask to a CVAT shape format.

        Args:
            frame: The frame number this mask appears in
            label_id: The ID of the label this mask is associated with
            group: The group ID for this shape

        Returns:
            LabeledShapeRequest object for CVAT API
        """
        # Convert RLE string to list of floats
        points = [float(x) for x in self.rle.split(",")]

        # Get the full mask to find the actual bounding box
        mask = self.segmentation(height=2048, width=4096)

        # Find the bounding box coordinates
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        top = np.where(rows)[0][0]
        bottom = np.where(rows)[0][-1]
        left = np.where(cols)[0][0]
        right = np.where(cols)[0][-1]

        # Add bounding box coordinates
        points.extend(
            [
                float(left),  # x-offset
                float(top),  # y-offset
                float(right),  # right coordinate
                float(bottom),  # bottom coordinate
            ]
        )

        return models.LabeledShapeRequest(
            type="mask",
            occluded=bool(self.occluded),
            z_order=self.z_order,
            points=points,
            rotation=0.0,
            outside=False,
            attributes=[attr.model_dump() for attr in self.attributes],
            group=group,
            source=self.source,
            frame=frame,
            label_id=label_id,
        )

    def pil_image(
        self, height: int | None = None, width: int | None = None
    ) -> Image.Image:
        """
        Convert the mask to a PIL Image.

        Args:
            height: Optional height of the output image. If None, uses the mask's height
            width: Optional width of the output image. If None, uses the mask's width

        Returns:
            PIL Image containing the mask (black and white)
        """
        if height is None and width is None:
            # If no dimensions provided, use the cropped mask
            mask_array = self.rle_decode()
        else:
            # If dimensions provided, use full segmentation
            mask_array = self.segmentation(
                height=height or self.height, width=width or self.width
            )

        # Convert boolean array to uint8 (0 and 255)
        mask_array = mask_array.astype(np.uint8) * 255
        return Image.fromarray(mask_array, mode="L")

    def _repr_html_(self) -> str:
        img = self.pil_image()
        import base64
        from io import BytesIO

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return f"""
        <div style="
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 800px;
            margin: 20px 0;
            background: #f8f9fa;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="
                padding: 15px;
                background: #ffffff;
                border-bottom: 1px solid #eee;">
                <div style="color: #444; line-height: 1.6;">
                    <span style="color: #666; display: inline-block; width: 80px;">Label:</span>
                    <span style="font-weight: 500;">{self.label}</span><br>
                    <span style="color: #666; display: inline-block; width: 80px;">Position:</span>
                    <span style="font-weight: 500;">({self.left}, {self.top})</span><br>
                    <span style="color: #666; display: inline-block; width: 80px;">Size:</span>
                    <span style="font-weight: 500;">{self.width} × {self.height}px</span><br>
                    <span style="color: #666; display: inline-block; width: 80px;">Z-order:</span>
                    <span style="font-weight: 500;">{self.z_order}</span>
                </div>
            </div>
            <div style="padding: 15px; text-align: center;">
                <img src="data:image/png;base64,{img_str}" 
                     style="max-width: 100%; height: auto; border-radius: 4px;" />
            </div>
        </div>
        """


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
