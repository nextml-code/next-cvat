from datetime import datetime
from pathlib import Path

import pytest

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
    finally:
        # Clean up - delete the task
        print(f"Cleaning up - deleting task {task.id}")
        project.delete_task_(task.id)
        print(f"Deleted task {task.id}")
