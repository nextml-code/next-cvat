from __future__ import annotations

from typing import TYPE_CHECKING

from cvat_sdk.api_client import models
from pydantic import BaseModel

from .job_annotations import JobAnnotations

if TYPE_CHECKING:
    from .task import Task


class Job(BaseModel):
    task: Task
    id: int

    def cvat(self) -> models.TaskRead:
        with self.task.project.client.cvat_client() as cvat_client:
            return cvat_client.jobs.retrieve(self.id)

    def annotations(self) -> JobAnnotations:
        with self.task.project.client.cvat_client() as cvat_client:
            return JobAnnotations(
                job=self,
                annotations=cvat_client.jobs.retrieve(self.id).get_annotations(),
            )

    def update_annotations_(self, annotations: JobAnnotations):
        with self.task.project.client.cvat_client() as cvat_client:
            annotations_request = annotations.request()
            # annotations_request = models.LabeledDataRequest()
            # annotations_request.version = annotations.version
            # annotations_request.tags = annotations.tags
            # annotations_request.shapes = annotations.shapes
            # annotations_request.tracks = annotations.tracks

            return cvat_client.jobs.retrieve(self.id).set_annotations(
                annotations_request
            )

    def job(self, job_id: int) -> Job:
        return Job(task=self, id=job_id)
