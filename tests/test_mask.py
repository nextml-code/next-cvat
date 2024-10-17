from pathlib import Path

import numpy as np
from PIL import Image

from next_cvat import Annotations


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
