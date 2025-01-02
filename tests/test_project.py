from pathlib import Path

import pytest

from next_cvat import Client


def test_download_includes_job_status(tmp_path):
    """Test that project download includes job status information."""
    if not Path(".env.cvat.secrets").exists():
        pytest.skip("No .env.cvat.secrets file found")

    cvat_client = Client.from_env_file(".env.cvat.secrets")

    # Get a test project
    project = cvat_client.project(217969)
    
    # Download the project
    project.download_(tmp_path)
    
    # Check that job_status.json exists and contains the expected fields
    status_file = tmp_path / "job_status.json"
    assert status_file.exists(), "job_status.json should be created"
    
    import json
    job_status = json.loads(status_file.read_text())
    
    # Check that we got a list of jobs
    assert isinstance(job_status, list), "job_status should be a list"
    
    # Check that each job has the required fields
    for job in job_status:
        assert "task_id" in job
        assert "job_id" in job
        assert "task_name" in job
        assert "stage" in job
        assert "state" in job
        assert "assignee" in job 