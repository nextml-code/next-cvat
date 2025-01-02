# Job Status

The `JobStatus` class tracks the status of annotation jobs in CVAT.

## Properties

- `task_id: str` - ID of the task this job belongs to
- `job_id: int` - Unique identifier for the job
- `task_name: str` - Name of the parent task
- `stage: str` - Current stage of the job (e.g., "annotation", "validation")
- `state: str` - Current state of the job (e.g., "completed", "in_progress")
- `assignee: Optional[Union[str, Dict[str, Any]]]` - Username or details of the person assigned to the job

## Usage

### Creating from Job Status Data

```python
status = JobStatus(
    task_id="906591",
    job_id=520016,
    task_name="Batch 1",
    stage="annotation",
    state="completed",
    assignee="john.doe"
)
```

### Creating from CVAT SDK Job Object

```python
status = JobStatus.from_job(job, task_name="Batch 1")
print(status.assignee_email)  # Get assignee's email
```

## Methods

### from_job

```python
@classmethod
def from_job(cls, job, task_name: str) -> JobStatus
```

Create a JobStatus from a CVAT SDK job object.

### assignee_email

```python
@property
def assignee_email(self) -> Optional[str]
```

Get the assignee's email if available. Returns the username from the assignee dictionary or the assignee string directly.
