# next-cvat

Downloads and decodes annotations on the format "CVAT for images 1.1".

## Usage

Either add environment variables to your global environment or create an env file.

```bash
CVAT_USERNAME=username
CVAT_PASSWORD=password
```

If you don't want to use your username and password, you can create a token:

```bash
cvat create-token
```

And use it like this:

```bash
CVAT_TOKEN=token
```

_Note that the token expires in 14 days._

### Download dataset

```python
import next_cvat

if __name__ == "__main__":
    (
        next_cvat.Client.from_env_file(".env.cvat.secrets")
        .project(1234)
        .download_(dataset_path="dataset-path")
    )
```

or using CLI:

```bash
cvat download --project-id <project-id> --dataset-path <dataset-path>
```

### Load annotations

And then load annotations:

```python
from next_cvat import Annotations

annotations = Annotations.from_path("dataset-path/annotations.xml")
```

### Upload images

Create a new task and upload images to it:

```python
import next_cvat
from pathlib import Path

client = next_cvat.Client.from_env()

# Create a new task
task = client.create_task("My Task", project_id=1234)

# Upload images
client.upload_images_(
    task.id,
    [
        Path("images/image1.jpg"),
        Path("images/image2.jpg"),
    ]
)
```

### Update annotations

```python
client = next_cvat.Client.from_env_file(".env.cvat.secrets")

job = client.project(project_id).task(task_id).job(job_id)

annotations = job.annotations()

annotations.add_mask_(
    next_cvat.Mask.from_segmentation(
        segmentation=Image.open("tests/test_vegetation_mask.png"),
        label="Deformation",
    ),
    image_name="20240916_000854_2011T_437.bmp",
)

job.update_annotations_(annotations)
```

### Delete frames

Delete a frame from a task:

```python
# Get a frame by its index (0-based) or by name
frame = task.frame(frame_id=0)  # or task.frame(name="image1.jpg")

# Delete the frame
task.delete_frame_(frame.id)
```

### Low-level API

```python
from next_cvat import Client

client = Client.from_env_file(".env.cvat.secrets")

with client.cvat_client() as cvat_client:
    cvat_client.get_tasks()
```
