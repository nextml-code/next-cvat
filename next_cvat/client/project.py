from __future__ import annotations

import json
import tempfile
import zipfile
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Generator, Union

from cvat_sdk import Client as CVATClient
from cvat_sdk.api_client import models
from cvat_sdk.core.proxies.projects import Project as CVATProject
from pydantic import BaseModel

from ..types.job_status import JobStatus
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

    def download_(self, dataset_path: Union[str, Path]) -> None:
        """Download project data to a local directory."""
        print(f"Downloading project {self.id} to dataset")
        dataset_path = Path(dataset_path)
        dataset_path.mkdir(exist_ok=True)

        with self.client.cvat_client() as cvat_client:
            # Get job status for all tasks
            job_status = []
            for task in self.tasks():
                try:
                    cvat_task = cvat_client.tasks.retrieve(task.id)
                    task_name = cvat_task.name
                    for job in task.jobs():
                        try:
                            cvat_job = cvat_client.jobs.retrieve(job.id)
                            job_status.append(JobStatus.from_job(cvat_job, task_name))
                        except Exception as e:
                            print(f"Error getting job status for job {job.id}: {e}")
                except Exception as e:
                    print(f"Error getting task {task.id}: {e}")

            # Save job status
            with open(dataset_path / "job_status.json", "w") as f:
                json.dump([status.model_dump() for status in job_status], f)

            # Download annotations for each task
            for task in self.tasks():
                try:
                    cvat_task = cvat_client.tasks.retrieve(task.id)
                    task_name = cvat_task.name
                    print(f"\nProcessing task: {task_name} (ID: {task.id})")
                    task_path = dataset_path / task_name
                    task_path.mkdir(exist_ok=True)

                    # Download frames
                    try:
                        for frame in task.frames():
                            print(f"\nFrame info: {frame.frame_info}")
                            print(f"Frame ID: {frame.id}")
                            print(f"Frame attributes: {dir(frame)}")
                            
                            frame_path = task_path / frame.frame_info['name']
                            print(f"Saving frame to: {frame_path}")
                            
                            try:
                                frame_data = cvat_task.get_frame(frame.id)
                                print(f"Frame data type: {type(frame_data)}")
                                print(f"Frame data attributes: {dir(frame_data)}")
                                
                                with open(frame_path, "wb") as f:
                                    data = frame_data.read()
                                    print(f"Read data type: {type(data)}")
                                    print(f"Read data length: {len(data)}")
                                    f.write(data)
                                    print("Successfully wrote frame data")
                            except Exception as e:
                                print(f"Error saving frame: {e}")
                                import traceback
                                traceback.print_exc()
                    except Exception as e:
                        print(f"Error getting frames for task {task.id}: {e}")

                    # Save annotations
                    print("\nSaving annotations")
                    try:
                        # Create a temporary file path but don't open it
                        temp_file = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
                        temp_file.close()
                        try:
                            annotations = cvat_task.export_dataset(
                                format_name="CVAT for images 1.1",
                                include_images=False,
                                filename=temp_file.name,
                            )
                            with open(task_path / "annotations.json", "wb") as f:
                                f.write(annotations.read())
                            print("Successfully saved annotations")
                        finally:
                            # Clean up the temporary file
                            Path(temp_file.name).unlink(missing_ok=True)
                    except Exception as e:
                        print(f"Error saving annotations: {e}")
                        import traceback
                        traceback.print_exc()
                except Exception as e:
                    print(f"Error processing task {task.id}: {e}")
                    import traceback
                    traceback.print_exc()

    def create_task_(
        self,
        name: str,
        image_quality: int = 70,
    ) -> Task:
        """
        Create a new task in this project.
        
        Args:
            name: Name of the task
            image_quality: Image quality (0-100) for compressed images
            
        Returns:
            Task object representing the created task
        """
        with self.client.cvat_client() as client:
            # Get project details to get the organization ID
            project = client.projects.retrieve(self.id)
            
            # Set organization header
            client.api_client.set_default_header('X-Organization', 'NextMLAB')
            
            # Create task in the project
            spec = models.TaskWriteRequest(
                name=name,
                project_id=self.id,
                organization=project.organization,
                image_quality=image_quality,
                status="annotation",
            )
            task = client.tasks.create(spec=spec)
            return Task(project=self, id=task.id)

    def task(self, task_id: int) -> Task:
        return Task(project=self, id=task_id)

    def tasks(self) -> list[Task]:
        with self.client.cvat_client() as cvat_client:
            project = cvat_client.projects.retrieve(self.id)
            return [Task(project=self, id=task.id) for task in project.get_tasks()]

    def __hash__(self) -> int:
        return hash(self.model_dump_json())

    @lru_cache
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

    def delete_task_(self, task_id: int) -> None:
        """
        Delete a task from this project.
        
        Args:
            task_id: ID of the task to delete
        """
        with self.client.cvat_client() as client:
            client.tasks.remove_by_ids([task_id])
