import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from next_cvat.client.client import Client


@pytest.fixture
def cvat_client():
    """Create a CVAT client for testing."""
    load_dotenv(".env.cvat.secrets")
    return Client(
        username=os.getenv("CVAT_USERNAME"),
        password=os.getenv("CVAT_PASSWORD"),
    ) 