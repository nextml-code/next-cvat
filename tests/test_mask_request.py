import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from next_cvat.types.mask import Mask


@pytest.fixture
def vegetation_mask_path() -> Path:
    return Path("tests/test_vegetation_mask.png")


@pytest.fixture
def vegetation_mask_json_path() -> Path:
    return Path("tests/test_vegetation_mask.json")


def test_mask_request_matches_json(
    vegetation_mask_path: Path, vegetation_mask_json_path: Path
):
    """Test that converting a mask image to a request matches the expected JSON format"""
    # Load the mask image
    mask_img = Image.open(vegetation_mask_path)

    # Load the expected JSON
    with vegetation_mask_json_path.open() as f:
        expected_json = json.load(f)

    # Create mask object
    mask = Mask.from_segmentation(
        label="vegetation",
        source="file",
        occluded=0,
        z_order=0,
        segmentation=mask_img,
        attributes=[],
    )

    # Create the request
    request = mask.request(
        frame=0,
        label_id=3683899,
        group=0,
    )

    # Convert request to dict for comparison
    request_dict = request.to_dict()

    # Debug print the points
    print("\nGenerated points length:", len(request_dict["points"]))
    print("Expected points length:", len(expected_json["points"]))

    # Print first few points from both
    print("\nFirst 10 generated points:", request_dict["points"][:10])
    print("First 10 expected points:", expected_json["points"][:10])

    # Print last few points from both
    print("\nLast 10 generated points:", request_dict["points"][-10:])
    print("Last 10 expected points:", expected_json["points"][-10:])

    # Compare other fields first
    assert request_dict["type"] == expected_json["type"]
    assert request_dict["frame"] == expected_json["frame"]
    assert request_dict["label_id"] == expected_json["label_id"]
    assert request_dict["occluded"] == expected_json["occluded"]
    assert request_dict["z_order"] == expected_json["z_order"]
    assert request_dict["rotation"] == expected_json["rotation"]
    assert request_dict["outside"] == expected_json["outside"]
    assert request_dict["attributes"] == expected_json["attributes"]
    assert request_dict["group"] == expected_json["group"]
    assert request_dict["source"] == expected_json["source"]

    # Compare points with more detailed error message
    assert request_dict["points"] == expected_json["points"], (
        f"\nPoints length mismatch: {len(request_dict['points'])} vs {len(expected_json['points'])}"
        f"\nFirst differing points at index: {next(i for i, (a, b) in enumerate(zip(request_dict['points'], expected_json['points'])) if a != b)}"
    )
