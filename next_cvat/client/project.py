from __future__ import annotations

import tempfile
import zipfile
from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator

from cvat_sdk import Client as CVATClient
from cvat_sdk.api_client import models
from cvat_sdk.core.proxies.projects import Project as CVATProject
from pydantic import BaseModel

from .task import Task

if TYPE_CHECKING:
    from next_cvat.client import Client


class Project(BaseModel):
    client: Client
    id: int

    @contextmanager
    def cvat(self) -> Generator[CVATProject, None, None]:
        with self.client.cvat_client() as client:
            yield client.projects.retrieve(self.id)

    def download_(self, dataset_path) -> Project:
        with self.client.cvat_client() as cvat_client:
            cvat_client: CVATClient

            project = cvat_client.projects.retrieve(self.id)

            print(f"Downloading project {self.id} to {dataset_path}")
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file_path = f"{temp_dir}/dataset.zip"
                project.export_dataset(
                    format_name="CVAT for images 1.1",
                    filename=temp_file_path,
                    include_images=True,
                )

                with zipfile.ZipFile(temp_file_path, "r") as zip_ref:
                    zip_ref.extractall(dataset_path)

        return self

    def create_task_(self, name: str):
        pass

    def task(self, task_id: int) -> Task:
        return Task(project=self, id=task_id)

    def tasks(self) -> list[Task]:
        with self.client.cvat_client() as cvat_client:
            project = cvat_client.projects.retrieve(self.id)
            print("count", project.tasks.count)
            print("tasks", project.get_tasks())
            return [Task(project=self, id=task.id) for task in project.get_tasks()]

    def labels(
        self, id: int | None = None, name: str | None = None
    ) -> list[models.Label]:
        with self.cvat() as cvat_project:
            labels = cvat_project.get_labels()

            if id is not None:
                labels = [label for label in labels if label.id == id]

            if name is not None:
                labels = [label for label in labels if label.name == name]

            return labels

    def label(self, name: str) -> models.Label:
        labels = self.labels(name=name)

        if len(labels) == 0:
            raise ValueError(f"Label with name {name} not found")
        elif len(labels) >= 2:
            raise ValueError(f"Multiple labels found with name {name}")
        else:
            return labels[0]
