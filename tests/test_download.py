import tempfile
from pathlib import Path

import pytest

import next_cvat


def test_download():
    if not Path(".env.cvat.secrets").exists():
        pytest.skip("No .env.cvat.secrets file found")

    with tempfile.TemporaryDirectory() as temp_dir:
        next_cvat.Client.from_env_file(".env.cvat.secrets").download_(
            project_id=188733,
            dataset_path=temp_dir,
        )
