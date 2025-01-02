# Working with Tasks

This guide shows you how to work with CVAT tasks using next-cvat.

## Creating Tasks

You can create new tasks in a project:

```python
from next_cvat.client.client import Client

# Initialize client and get project
client = Client.from_env_file(".env.cvat.secrets")
project = client.project(217969)  # Use test project

# Create a new task
task = project.create_task_(
    name="Test Task",
    image_quality=70,  # Optional: Set image quality (0-100)
)
print(f"Created task with ID: {task.id}")
project.delete_task_(task.id)  # Clean up
```

## Uploading Images

You can upload images to a task:

```python
from next_cvat.client.client import Client
import numpy as np
from PIL import Image
from pathlib import Path
import tempfile

# Initialize client and get project
client = Client.from_env_file(".env.cvat.secrets")
project = client.project(217969)  # Use test project

# Create a temporary test image
with tempfile.TemporaryDirectory() as tmp_dir:
    test_image = Path(tmp_dir) / "test_image.png"
    img = Image.new('RGB', (100, 100), color='white')
    pixels = np.array(img)
    pixels[40:60, 40:60] = [255, 0, 0]  # Red square
    Image.fromarray(pixels).save(test_image)

    # Create a new task for testing
    task = project.create_task_(name="Test Upload Task")

    try:
        # Upload the image
        task.upload_images_(
            image_paths=test_image,
            image_quality=70,  # Optional: Set image quality (0-100)
        )

        # Verify upload
        frames = task.frames()
        assert len(frames) == 1
        print("Successfully uploaded and verified frame")
    finally:
        # Clean up
        project.delete_task_(task.id)
```

## Working with Frames

You can access and manipulate frames in a task:

```python
from next_cvat.client.client import Client
import numpy as np
from PIL import Image
from pathlib import Path
import tempfile

# Initialize client and get project
client = Client.from_env_file(".env.cvat.secrets")
project = client.project(217969)  # Use test project

# Create a new task for testing
task = project.create_task_(name="Test Frames Task")

try:
    # Upload a test image
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_image = Path(tmp_dir) / "test_image.png"
        img = Image.new('RGB', (100, 100), color='white')
        pixels = np.array(img)
        pixels[40:60, 40:60] = [255, 0, 0]  # Red square
        Image.fromarray(pixels).save(test_image)
        task.upload_images_(image_paths=test_image)

    # List all frames
    frames = task.frames()
    assert len(frames) == 1
    print(f"Number of frames: {len(frames)}")

    # Get a specific frame by ID
    frame = task.frame(frame_id=0)  # Get first frame
    assert frame is not None
    print(f"Frame name: {frame.frame_info['name']}")
    print(f"Frame size: {frame.frame_info['width']}x{frame.frame_info['height']}")
finally:
    # Clean up
    project.delete_task_(task.id)
```

## Deleting Frames

You can delete frames from a task:

```python
from next_cvat.client.client import Client
import numpy as np
from PIL import Image
from pathlib import Path
import tempfile

# Initialize client and get project
client = Client.from_env_file(".env.cvat.secrets")
project = client.project(217969)  # Use test project

# Create a new task for testing
task = project.create_task_(name="Test Delete Frame Task")

try:
    # Upload a test image
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_image = Path(tmp_dir) / "test_image.png"
        img = Image.new('RGB', (100, 100), color='white')
        pixels = np.array(img)
        pixels[40:60, 40:60] = [255, 0, 0]  # Red square
        Image.fromarray(pixels).save(test_image)
        task.upload_images_(image_paths=test_image)

    # Delete a frame by ID
    frames = task.frames()
    assert len(frames) == 1
    frame_id = 0  # ID of the frame to delete
    task.delete_frame_(frame_id)
    print(f"Deleted frame {frame_id}")

    # Verify deletion
    frames = task.frames()
    assert len(frames) == 0
finally:
    # Clean up
    project.delete_task_(task.id)
```

## Getting Task Jobs

You can access the jobs associated with a task:

```python
from next_cvat.client.client import Client
import numpy as np
from PIL import Image
from pathlib import Path
import tempfile

# Initialize client and get project
client = Client.from_env_file(".env.cvat.secrets")
project = client.project(217969)  # Use test project

# Create a new task for testing
task = project.create_task_(name="Test Jobs Task")

try:
    # Upload a test image
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_image = Path(tmp_dir) / "test_image.png"
        img = Image.new('RGB', (100, 100), color='white')
        pixels = np.array(img)
        pixels[40:60, 40:60] = [255, 0, 0]  # Red square
        Image.fromarray(pixels).save(test_image)
        task.upload_images_(image_paths=test_image)

    # List all jobs
    jobs = task.jobs()
    assert len(jobs) == 1
    for job in jobs:
        assert job.id is not None
        print(f"Job ID: {job.id}")
        print(f"State: {job.state()}")
        print(f"Stage: {job.stage()}")
finally:
    # Clean up
    project.delete_task_(task.id)
```

Each code block in this documentation is automatically tested to ensure it works correctly.
