# Working with Jobs

This guide shows you how to work with CVAT jobs using Next CVAT.

## Getting Job Information

You can get information about a job:

```python
from next_cvat.client.client import Client
import numpy as np
from PIL import Image
from pathlib import Path
import tempfile

# Initialize client and get project
client = Client.from_env_file(".env.cvat.secrets")
project = client.project(217969)  # Use test project

# Create a task with an image
task = project.create_task_(name="Test Job Info")

try:
    # Upload a test image
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_image = Path(tmp_dir) / "test_image.png"
        img = Image.new('RGB', (100, 100), color='white')
        pixels = np.array(img)
        pixels[40:60, 40:60] = [255, 0, 0]  # Red square
        Image.fromarray(pixels).save(test_image)
        task.upload_images_(image_paths=test_image)

    # Get the job
    jobs = task.jobs()
    assert len(jobs) == 1
    job = jobs[0]

    # Get job information
    print(f"Job ID: {job.id}")
    print(f"State: {job.state()}")
    print(f"Stage: {job.stage()}")
finally:
    # Clean up
    project.delete_task_(task.id)
```

## Working with Annotations

You can get and update annotations for a job:

```python
from next_cvat.client.client import Client
from next_cvat.client.job_annotations import JobAnnotations
import numpy as np
from PIL import Image
from pathlib import Path
import tempfile

# Initialize client and get project
client = Client.from_env_file(".env.cvat.secrets")
project = client.project(217969)  # Use test project

# Create a task with an image
task = project.create_task_(name="Test Job Annotations")

try:
    # Upload a test image
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_image = Path(tmp_dir) / "test_image.png"
        img = Image.new('RGB', (100, 100), color='white')
        pixels = np.array(img)
        pixels[40:60, 40:60] = [255, 0, 0]  # Red square
        Image.fromarray(pixels).save(test_image)
        task.upload_images_(image_paths=test_image)

    # Get the job
    jobs = task.jobs()
    assert len(jobs) == 1
    job = jobs[0]

    # Get annotations
    annotations = job.annotations()
    print(f"Initial annotations: {annotations}")

    # Create new annotations
    new_annotations = JobAnnotations(
        job=job,
        annotations={
            "version": 0,
            "tags": [],
            "shapes": [
                {
                    "type": "rectangle",
                    "occluded": False,
                    "points": [40, 40, 60, 60],
                    "frame": 0,
                    "label_id": project.labels()[0].id,
                    "group": 0,
                    "source": "manual",
                    "attributes": []
                }
            ],
            "tracks": []
        }
    )

    # Update annotations
    job.update_annotations_(new_annotations)
    print("Updated annotations successfully")

    # Verify update
    updated_annotations = job.annotations()
    assert len(updated_annotations.annotations["shapes"]) == 1
    print("Verified annotations update")
finally:
    # Clean up
    project.delete_task_(task.id)
```

## Getting Job Status

You can check the status of a job:

```python
from next_cvat.client.client import Client
import numpy as np
from PIL import Image
from pathlib import Path
import tempfile

# Initialize client and get project
client = Client.from_env_file(".env.cvat.secrets")
project = client.project(217969)  # Use test project

# Create a task with an image
task = project.create_task_(name="Test Job Status")

try:
    # Upload a test image
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_image = Path(tmp_dir) / "test_image.png"
        img = Image.new('RGB', (100, 100), color='white')
        pixels = np.array(img)
        pixels[40:60, 40:60] = [255, 0, 0]  # Red square
        Image.fromarray(pixels).save(test_image)
        task.upload_images_(image_paths=test_image)

    # Get the job
    jobs = task.jobs()
    assert len(jobs) == 1
    job = jobs[0]

    # Get job status
    print(f"Job state: {job.state()}")
    print(f"Job stage: {job.stage()}")
finally:
    # Clean up
    project.delete_task_(task.id)
```

Each code block in this documentation is automatically tested to ensure it works correctly.
