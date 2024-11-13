from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Generator

from cvat_sdk.core.proxies.tasks import Task as CVATTask
from pydantic import BaseModel

from .frame import Frame
from .job import Job

if TYPE_CHECKING:
    from .project import Project


class Task(BaseModel):
    project: Project
    id: int

    @contextmanager
    def cvat(self) -> Generator[CVATTask, None, None]:
        with self.project.client.cvat_client() as cvat_client:
            yield cvat_client.tasks.retrieve(self.id)

    def create_job_(self, name: str):
        pass

    def job(self, job_id: int) -> Job:
        return Job(task=self, id=job_id)

    def frame(
        self,
        frame_id: int | None = None,
        name: str | None = None,
        image_name: str | None = None,
    ) -> Frame:
        frames = self.frames()

        frames = [
            frame
            for frame in frames
            if (frame.id == frame_id or frame_id is None)
            and (frame.frame_info.name == name or name is None)
            and (Path(frame.frame_info.name).name == image_name or image_name is None)
        ]

        if len(frames) >= 2:
            raise ValueError(
                f"Multiple frames found with id {frame_id} and name {name}"
            )
        elif len(frames) == 0:
            raise ValueError(f"Frame with id {frame_id} and name {name} not found")
        else:
            return frames[0]

    def frames(self) -> list[Frame]:
        with self.cvat() as cvat_task:
            return [
                Frame(task=self, id=frame_id, frame_info=frame_info)
                for frame_id, frame_info in enumerate(cvat_task.get_frames_info())
            ]
