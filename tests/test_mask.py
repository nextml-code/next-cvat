from pathlib import Path

import numpy as np
from PIL import Image

from next_cvat import Annotations
from next_cvat.types.mask import Mask


def test_mask_annotations():
    annotations_data = Annotations.from_path("tests/mask_annotations.xml")
    assert len(annotations_data.images) == 1
    assert len(annotations_data.images[0].masks) == 3

    image = annotations_data.images[0]
    first_mask = image.masks[0]
    assert first_mask.label == "vegetation"
    ground_truth = np.array(Image.open("tests/test_vegetation_mask.png")) == 255
    mask = first_mask.segmentation(image.height, image.width)
    assert np.allclose(first_mask.segmentation(image.height, image.width), ground_truth)


def test_mask_from_rgba():
    # Create a simple RGBA test image
    rgba_array = np.zeros((10, 10, 4), dtype=np.uint8)
    # Set a 3x3 square in the middle to white with 50% opacity
    rgba_array[3:6, 3:6] = [255, 255, 255, 128]
    
    # Create mask from RGBA array
    mask = Mask.from_segmentation(rgba_array, label="test")
    
    # Expected result: the 3x3 square should be True, rest False
    expected = np.zeros((10, 10), dtype=bool)
    expected[3:6, 3:6] = True
    
    # Check if the segmentation matches our expectation
    result = mask.segmentation(height=10, width=10)
    assert np.array_equal(result, expected), "RGBA mask conversion failed"
    
    # Also test with PIL Image
    rgba_image = Image.fromarray(rgba_array, mode='RGBA')
    mask_from_pil = Mask.from_segmentation(rgba_image, label="test")
    result_from_pil = mask_from_pil.segmentation(height=10, width=10)
    assert np.array_equal(result_from_pil, expected), "RGBA PIL Image mask conversion failed"
