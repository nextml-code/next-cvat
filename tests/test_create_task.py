from datetime import datetime
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

import next_cvat


def test_create_task():
    if not Path(".env.cvat.secrets").exists():
        pytest.skip("No secrets file found")

    client = next_cvat.Client.from_env_file(".env.cvat.secrets")
    
    # Use the dedicated test project
    project_id = 217969
    project = client.project(project_id)

    # Create a test task with unique name
    task_name = f"Test Task {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    task = project.create_task_(task_name)
    assert task.id is not None
    print(f"Created task {task.id} with name {task_name}")

    # Create a small test image
    test_image = Image.fromarray(np.zeros((100, 100), dtype=np.uint8))
    with Path("test_image.png").open("wb") as f:
        test_image.save(f)

    try:
        # Upload the test image
        task.upload_images_("test_image.png")

        # Verify the image was uploaded by checking frames
        frames = task.frames()
        assert len(frames) == 1
        assert frames[0].frame_info.height == 100
        assert frames[0].frame_info.width == 100

        # Verify that the task appears in the project's tasks list
        project_tasks = project.tasks()
        task_ids = [t.id for t in project_tasks]
        assert task.id in task_ids, f"Task {task.id} not found in project tasks {task_ids}"
        
        # Verify task details
        with client.cvat_client() as cvat:
            task_details = cvat.tasks.retrieve(task.id)
            assert task_details.name == task_name, f"Task name mismatch: {task_details.name} != {task_name}"
            assert task_details.project_id == project_id, f"Project ID mismatch: {task_details.project_id} != {project_id}"
            print(f"Verified task {task.id} exists in project {project_id} with name '{task_name}'")

    finally:
        # Cleanup
        Path("test_image.png").unlink()
        try:
            project.delete_task_(task.id)
            print(f"Deleted task {task.id}")
        except Exception as e:
            print(f"Failed to delete task {task.id}: {e}") 