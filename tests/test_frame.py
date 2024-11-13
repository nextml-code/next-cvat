from pathlib import Path

import pytest

import next_cvat


def test_frame():
    if not Path(".env.cvat.secrets").exists():
        pytest.skip("No secrets file found")

    client = next_cvat.Client.from_env_file(".env.cvat.secrets")

    project_id = 198488
    task_id = 999670

    client.project(project_id).task(task_id).frames()[0]._repr_html_()
