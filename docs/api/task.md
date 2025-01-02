# Task

The `Task` class represents a unit of work for annotation in CVAT.

## Properties

- `task_id: str` - Unique identifier for the task
- `name: str` - Human-readable name of the task
- `url: Optional[str]` - Optional URL to access the task's data or API endpoint

## Usage

```python
task = Task(
    task_id="906591",
    name="Batch 1",
    url="https://app.cvat.ai/api/jobs/520016"
)
```

## Methods

### job_id

```python
def job_id(self) -> str
```

Extracts the job ID from the task's URL. Assumes the job ID is the last numeric part of the URL.
