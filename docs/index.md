# next-cvat

A Python library for interacting with CVAT (Computer Vision Annotation Tool).

## Installation

```bash
pip install next-cvat
```

## Quick Start

```python
from next_cvat import Client

# Initialize client from environment variables
client = Client.from_env_file(".env.cvat.secrets")

# Get a project
project = client.project(217969)

# Download project data
project.download_("dataset/")

# Load annotations
from next_cvat import Annotations
annotations = Annotations.from_path("dataset/annotations.xml")
```

## Features

- Easy-to-use Python interface for CVAT
- Support for projects, tasks, jobs, and annotations
- Download and upload functionality
- Mask annotation support
- Job status tracking
- Comprehensive type hints and documentation

## API Reference

### Annotations

The `Annotations` class provides functionality to load, save and query CVAT annotations:

```python
# Load annotations from XML file
annotations = Annotations.from_path("annotations.xml")

# Load annotations with job status
annotations = Annotations.from_path(
    "annotations.xml",
    "job_status.json"
)

# Get completed tasks and their images
completed_tasks = annotations.get_completed_tasks()
completed_images = annotations.get_images_from_completed_tasks()

# Get task status
task_status = annotations.get_task_status("1234")
# Returns: {"5678": "completed", "5679": "in_progress"}

# Create CVAT link for an image
link = annotations.create_cvat_link("image1.jpg")
# Returns: "https://app.cvat.ai/tasks/453747/jobs/520016"
```

### Project

The `Project` class represents a CVAT project:

```python
project = Project(
    id="217969",
    name="My Project",
    created="2024-01-01 12:00:00.000000+00:00",
    updated="2024-01-01 12:00:00.000000+00:00",
    labels=[
        Label(name="car", color="#ff0000", type="any"),
        Label(name="person", color="#00ff00", type="any")
    ]
)
```

### Task

The `Task` class represents a unit of work for annotation:

```python
task = Task(
    task_id="906591",
    name="Batch 1",
    url="https://app.cvat.ai/api/jobs/520016"
)
```

### JobStatus

The `JobStatus` class tracks the status of annotation jobs:

```python
# Create from job status data
status = JobStatus(
    task_id="906591",
    job_id=520016,
    task_name="Batch 1",
    stage="annotation",
    state="completed",
    assignee="john.doe"
)

# Create from CVAT SDK job object
status = JobStatus.from_job(job, task_name="Batch 1")
print(status.assignee_email)  # Get assignee's email
```

### ImageAnnotation

The `ImageAnnotation` class represents annotations for a single image:

```python
image = ImageAnnotation(
    id="1",
    name="frame_000001.jpg",
    subset="train",
    task_id="906591",
    width=1920,
    height=1080,
    boxes=[
        Box(label="car", xtl=100, ytl=200, xbr=300, ybr=400)
    ],
    masks=[
        Mask(label="person", points="100,200;300,400", z_order=1)
    ]
)
```

### Box

The `Box` class represents a bounding box annotation:

```python
# Simple box
box = Box(
    label="car",
    xtl=100,
    ytl=200,
    xbr=300,
    ybr=400,
    occluded=False,
    z_order=1
)

# Box with attributes
box_with_attrs = Box(
    label="car",
    xtl=100,
    ytl=200,
    xbr=300,
    ybr=400,
    attributes=[
        Attribute(name="color", value="red"),
        Attribute(name="model", value="sedan")
    ]
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
