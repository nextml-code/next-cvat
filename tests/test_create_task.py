from datetime import datetime
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

import next_cvat


def test_create_task():
    if not Path(".env.cvat.secrets").exists():
        pytest.skip("No secrets file found")

    print("\nSetting up test...")
    client = next_cvat.Client.from_env_file(".env.cvat.secrets")

    # Use the dedicated test project
    project_id = 217969
    project = client.project(project_id)
    print(f"Using test project {project_id}")

    # Create a test task with unique name
    task_name = f"Test Task {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"Creating task with name: {task_name}")
    task = project.create_task_(task_name)
    print(f"Created task {task.id} with name {task_name}")

    try:
        # Verify task was created
        assert task.id is not None
        assert isinstance(task.id, int)
        print(f"Verified task {task.id} exists")

        # Create a small test image
        print("Creating test image...")
        test_image = Image.fromarray(np.zeros((100, 100), dtype=np.uint8))
        test_image_path = Path("test_image.png")
        test_image.save(test_image_path)

        # Upload the test image
        print(f"Uploading image to task {task.id}...")
        task.upload_images_(test_image_path)

        # Verify the image was uploaded
        frames = task.frames()
        assert len(frames) == 1, f"Expected 1 frame, got {len(frames)}"
        assert frames[0].frame_info.height == 100, f"Expected height 100, got {frames[0].frame_info.height}"
        assert frames[0].frame_info.width == 100, f"Expected width 100, got {frames[0].frame_info.width}"
        print("Verified image was uploaded successfully")

    finally:
        # Clean up
        print("Cleaning up...")
        if test_image_path.exists():
            test_image_path.unlink()
            print("Deleted test image")
        
        print(f"Deleting task {task.id}")
        project.delete_task_(task.id)
        print(f"Deleted task {task.id}")
