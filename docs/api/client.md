# Client

The `Client` class is the main entry point for interacting with CVAT through next-cvat.

## Features

- Initialize CVAT client from environment variables or credentials
- Access and manage projects, tasks, and jobs
- Download project data and annotations
- Upload annotations and frames
- Track job status

## Usage

### Initialization

```python
from next_cvat import Client

# Initialize from environment file
client = Client.from_env_file(".env.cvat.secrets")

# Initialize with credentials
client = Client(
    server_address="https://app.cvat.ai",
    username="user@example.com",
    password="password"
)
```

### Working with Projects

```python
# Get a project by ID
project = client.project(217969)

# Download project data
project.download_("dataset/")

# Get project tasks
tasks = project.tasks()
for task in tasks:
    print(f"Task {task.id}: {task.name}")
```

### Working with Tasks

```python
# Get a task by ID
task = client.task(906591)

# Create a new task
task = client.create_task(
    name="New Task",
    project_id=217969,
    frame_paths=["image1.jpg", "image2.jpg"]
)

# Delete a frame from a task
task.delete_frame("image1.jpg")
```

### Working with Jobs

```python
# Get a job by ID
job = client.job(520016)

# Get job annotations
annotations = job.annotations()

# Update job status
job.update_status("completed")
```

## API Reference

### Properties

- `server_address: str` - CVAT server URL
- `username: str` - Username for authentication
- `password: str` - Password for authentication

### Methods

#### from_env_file

```python
@classmethod
def from_env_file(cls, env_file: Union[str, Path]) -> Client
```

Initialize client from environment file containing CVAT credentials.

#### project

```python
def project(self, project_id: int) -> Project
```

Get a project by ID.

#### task

```python
def task(self, task_id: int) -> Task
```

Get a task by ID.

#### job

```python
def job(self, job_id: int) -> Job
```

Get a job by ID.

#### create_task

```python
def create_task(
    self,
    name: str,
    project_id: int,
    frame_paths: List[Union[str, Path]],
    **kwargs
) -> Task
```

Create a new task in a project with the given frames.

#### create_token

```python
def create_token(self) -> str
```

Create a new authentication token for the current user.
