from pathlib import Path

import pytest

import next_cvat


def test_client():
    if not Path(".env.cvat.secrets").exists():
        pytest.skip("No .env.cvat.secrets file found")

    client = next_cvat.Client.from_env_file(".env.cvat.secrets")
    projects = client.list_projects()
