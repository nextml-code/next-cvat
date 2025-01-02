# Examples

This guide shows you how to use next-cvat for common tasks.

## Authentication

Create a `.env.cvat.secrets` file with your CVAT credentials:

```bash skip
CVAT_HOST=https://app.cvat.ai
CVAT_USERNAME=your_username
CVAT_PASSWORD=your_password
```

## Basic Workflow

Here's a complete example showing the main features:

```python skip
from next_cvat import Client
from pathlib import Path

# Initialize client
client = Client.from_env_file(".env.cvat.secrets")

# Get a project
project = client.project(217969)  # Use test project

# Create a new task
task = project.create_task_(
    name="Test Task",
    image_quality=70
)

try:
    # Upload images (replace with your actual image paths)
    task.upload_images_(
        image_paths=["path/to/image1.jpg", "path/to/image2.jpg"],
        image_quality=70
    )

    # Get task jobs
    jobs = task.jobs()
    job = jobs[0]  # Get first job

    # Get and update annotations
    annotations = job.annotations()

    # Add a bounding box annotation
    new_annotations = {
        "version": 0,
        "tags": [],
        "shapes": [{
            "type": "rectangle",
            "points": [40, 40, 60, 60],
            "frame": 0,
            "label_id": project.labels()[0].id,
            "group": 0,
            "source": "manual",
            "attributes": []
        }],
        "tracks": []
    }
    job.update_annotations_(new_annotations)

    # Check job status
    print(f"Job state: {job.state()}")
    print(f"Job stage: {job.stage()}")

finally:
    # Clean up
    project.delete_task_(task.id)
```

## Working with Projects

```python skip
# Get project metadata
project = client.project(217969)
with project.cvat() as cvat_project:
    print(f"Project name: {cvat_project.name}")
    print(f"Created: {cvat_project.created_date}")

# List tasks in project
tasks = project.tasks()
for task in tasks:
    print(f"Task {task.id}: {task.name}")
```

## Working with Tasks

```python skip
# Get a specific task
task = client.task(906591)

# List frames in task
frames = task.frames()
print(f"Number of frames: {len(frames)}")

# Delete a frame
task.delete_frame_(0)  # Delete first frame
```

## Working with Jobs

```python skip
# Get a specific job
job = client.job(520016)

# Update job status
job.update_status("completed")

# Get job annotations
annotations = job.annotations()
print(f"Number of shapes: {len(annotations.annotations['shapes'])}")
```

Note: The code examples above are for illustration purposes. Replace the IDs and file paths with your actual values.
