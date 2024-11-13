from __future__ import annotations

import tempfile
import zipfile
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Generator

from cvat_sdk import Client as CVATClient
from cvat_sdk.api_client import models
from pydantic import BaseModel

import next_cvat

if TYPE_CHECKING:
    from .job import Job


class JobAnnotations(BaseModel, arbitrary_types_allowed=True):
    job: Job
    annotations: models.AnnotationsRead

    def cvat(self) -> models.AnnotationsRead:
        return self.annotations

    def add_mask_(
        self, mask: next_cvat.Mask, image_path: str, group: int = 0
    ) -> JobAnnotations:
        label = self.job.task.project.labels(name=mask.label)

        self.annotations.shapes.append(
            next_cvat.Mask.from_segmentation(
                label=label,
                source="automatic",
            ).request(
                frame=0,
                label_id=label.id,
                group=group,
            )
        )

        return self

    def request(self) -> models.LabeledDataRequest:
        request = models.LabeledDataRequest()
        request.version = self.annotations.version
        request.tags = self.annotations.tags
        request.shapes = self.annotations.shapes
        request.tracks = self.annotations.tracks
        return request


# with client.cvat_client() as cvat_client:
#     job = cvat_client.jobs.retrieve(job_id)

#     annotations = job.get_annotations()

#     request = models.LabeledDataRequest()
#     request.shapes = [
#         next_cvat.Mask.from_segmentation(
#             label="Deformation",
#             source="automatic",
#             occluded=0,
#             z_order=0,
#             segmentation=Image.open("tests/test_vegetation_mask.png"),
#             attributes=[],
#         ).request(
#             frame=0,
#             label_id=3683899,
#             group=0,
#         )
#     ]

#     job.set_annotations(request)
