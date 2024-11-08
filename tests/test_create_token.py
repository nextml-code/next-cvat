from pathlib import Path

import pytest

import next_cvat


def test_create_token():
    if not Path(".env.cvat.secrets").exists():
        pytest.skip("No .env.cvat.secrets file found")

    token = next_cvat.Client.from_env_file(".env.cvat.secrets").create_token()
