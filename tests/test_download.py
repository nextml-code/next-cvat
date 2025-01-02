import tempfile
from pathlib import Path

import pytest

import next_cvat


def test_download():
    if not Path(".env.cvat.secrets").exists():
        pytest.skip("No .env.cvat.secrets file found")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Use test project ID
        client = next_cvat.Client.from_env_file(".env.cvat.secrets")
        client.download_(
            project_id=217969,  # Using test project
            dataset_path=temp_dir,
        )
        
        temp_path = Path(temp_dir)
        
        # Check job status exists
        job_status_path = temp_path / "job_status.json"
        assert job_status_path.exists(), "job_status.json should exist"
        
        # Check annotations
        assert (temp_path / "annotations.xml").exists(), "annotations.xml missing"
        
        # Check images directory
        images_dir = temp_path / "images"
        assert images_dir.exists(), "images directory missing"
        
        # Check for actual images
        image_files = list(images_dir.glob("*"))
        assert len(image_files) > 0, "No images found in images directory"
        print(f"Found {len(image_files)} images")
