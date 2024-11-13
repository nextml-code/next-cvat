from __future__ import annotations

from typing import TYPE_CHECKING

from cvat_sdk.api_client import models
from pydantic import BaseModel

from .job import Job

if TYPE_CHECKING:
    from .project import Project


class Task(BaseModel):
    project: Project
    id: int

    def cvat(self) -> models.TaskRead:
        with self.project.client.cvat_client() as cvat_client:
            return cvat_client.tasks.retrieve(self.id)

    def create_job_(self, name: str):
        pass

    def job(self, job_id: int) -> Job:
        return Job(task=self, id=job_id)
