import tempfile
from pathlib import Path

import pytest

import next_cvat
from next_cvat import Annotations


def test_download():
    if not Path(".env.cvat.secrets").exists():
        pytest.skip("No .env.cvat.secrets file found")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Use test project ID with known annotations
        client = next_cvat.Client.from_env_file(".env.cvat.secrets")
        client.download_(
            project_id=198488,  # Project with test annotations
            dataset_path=temp_dir,
        )
        
        temp_path = Path(temp_dir)
        
        # Check job status exists
        job_status_path = temp_path / "job_status.json"
        assert job_status_path.exists(), "job_status.json should exist"
        
        # Check annotations
        annotations_path = temp_path / "annotations.xml"
        assert annotations_path.exists(), "annotations.xml missing"
        
        # Load annotations and verify they can be parsed
        annotations = Annotations.from_path(annotations_path)
        
        # Try to convert boxes to segmentations - this should reproduce the error
        for image in annotations.images:
            print(f"Processing image: {image.name}")
            for box in image.boxes:
                print(f"Converting box: {box.label}")
                # This should raise AttributeError: 'Box' object has no attribute 'source'
                mask = box.segmentation(height=2000, width=2000)  # Using example dimensions
        
        # Check images directory
        images_dir = temp_path / "images"
        assert images_dir.exists(), "images directory missing"
        
        # Check for actual images
        image_files = list(images_dir.glob("*"))
        assert len(image_files) > 0, "No images found in images directory"
        print(f"Found {len(image_files)} images")
