import os
from pathlib import Path

import pytest

from next_cvat.client.client import Client


@pytest.fixture
def client():
    """Return a CVAT client."""
    return Client.from_env_file(".env.cvat.secrets")

@pytest.fixture
def project(client):
    """Return a test project."""
    return client.project(217969)  # Use test project

@pytest.fixture
def tmp_image(tmp_path):
    """Create a temporary test image."""
    import numpy as np
    from PIL import Image
    
    test_image = tmp_path / "test_image.png"
    img = Image.new('RGB', (100, 100), color='white')
    pixels = np.array(img)
    pixels[40:60, 40:60] = [255, 0, 0]  # Red square
    Image.fromarray(pixels).save(test_image)
    return test_image

def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers",
        "codeblocks: mark test to be collected from code blocks",
    )
    
    # Register fixtures for code block tests
    config.addinivalue_line(
        "codeblocks_test_namespace",
        "client = client",
    )
    config.addinivalue_line(
        "codeblocks_test_namespace",
        "project = project",
    )
    config.addinivalue_line(
        "codeblocks_test_namespace",
        "tmp_image = tmp_image",
    ) 