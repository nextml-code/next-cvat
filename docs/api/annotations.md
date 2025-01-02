# Annotations

The `Annotations` class provides functionality to load, save and query CVAT annotations.

## Features

- Load and save CVAT XML annotation files
- Track job status information
- Query task completion status
- Access image annotations

## Usage

### Loading Annotations

```python
# Load annotations from XML file
annotations = Annotations.from_path("annotations.xml")

# Load annotations with job status
annotations = Annotations.from_path(
    "annotations.xml",
    "job_status.json"
)
```

### Querying Tasks and Images

```python
# Get completed tasks and their images
completed_tasks = annotations.get_completed_tasks()
completed_images = annotations.get_images_from_completed_tasks()

# Get task status
task_status = annotations.get_task_status("1234")
# Returns: {"5678": "completed", "5679": "in_progress"}
```

### Creating CVAT Links

```python
# Create CVAT link for an image
link = annotations.create_cvat_link("image1.jpg")
# Returns: "https://app.cvat.ai/tasks/453747/jobs/520016"
```

## API Reference

### Properties

- `version: str` - Version of the CVAT annotations format
- `project: Project` - Project metadata and labels
- `tasks: List[Task]` - List of tasks in the project
- `images: List[ImageAnnotation]` - List of image annotations
- `job_status: List[JobStatus]` - List of job status information

### Methods

#### from_path

```python
@classmethod
def from_path(
    cls,
    xml_annotation_path: Union[str, Path],
    job_status_path: Optional[Union[str, Path]] = None
) -> Annotations
```

Load annotations from XML file and optionally include job status information.

#### get_task_status

```python
def get_task_status(self, task_id: str) -> Dict[str, str]
```

Get the status of all jobs for a given task. Returns a dictionary mapping job IDs to their states.

#### get_completed_tasks

```python
def get_completed_tasks(self) -> List[Task]
```

Get all tasks that have all jobs completed. A task is considered completed when all of its jobs are in the "completed" state.

#### get_completed_task_ids

```python
def get_completed_task_ids(self) -> List[str]
```

Get IDs of all tasks that have all jobs completed.

#### get_images_from_completed_tasks

```python
def get_images_from_completed_tasks(self) -> List[ImageAnnotation]
```

Get all images from completed tasks.

#### create_cvat_link

```python
def create_cvat_link(self, image_name: str) -> str
```

Create a CVAT link for the given image name. Returns a link in the format: `https://app.cvat.ai/tasks/{task_id}/jobs/{job_id}`
