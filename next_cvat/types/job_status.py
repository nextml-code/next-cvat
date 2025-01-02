from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field


class JobStatus(BaseModel):
    """Status information for a job."""

    task_id: str
    job_id: int
    task_name: str
    stage: str
    state: str
    assignee: Optional[Union[str, Dict[str, Any]]] = None

    @classmethod
    def from_job(cls, job, task_name: str):
        """Create a JobStatus from a CVAT SDK job object."""
        assignee = job.assignee
        if hasattr(assignee, '__dict__'):
            assignee = {k: v for k, v in assignee.__dict__.items() if not k.startswith('_')}
        elif hasattr(assignee, 'to_dict'):
            assignee = assignee.to_dict()

        return cls(
            task_id=str(job.task_id),
            job_id=job.id,
            task_name=task_name,
            stage=job.stage,
            state=job.state,
            assignee=assignee,
        )

    @property
    def assignee_email(self) -> Optional[str]:
        """Get the assignee's email if available."""
        if isinstance(self.assignee, dict):
            return self.assignee.get('username')
        return self.assignee 