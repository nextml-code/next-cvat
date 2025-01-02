from typing import Optional

from pydantic import BaseModel


class JobStatus(BaseModel):
    """Status information for a job."""

    task_id: str
    job_id: int
    task_name: str
    stage: str
    state: str
    assignee: Optional[str] = None 