from __future__ import annotations

from pathlib import Path
from typing import List, Union
from xml.etree import ElementTree

from pydantic import BaseModel

from .types import (
    Attribute,
    Box,
    ImageAnnotation,
    Label,
    Mask,
    Polygon,
    Polyline,
    Project,
    Task,
)


class Annotations(BaseModel):
    version: str
    project: Project
    tasks: List[Task]
    images: List[ImageAnnotation]

    @classmethod
    def from_path(cls, xml_annotation_path: Union[str, Path]) -> Annotations:
        tree = ElementTree.parse(str(xml_annotation_path))
        root = tree.getroot()

        # Parse project details
        project = root.find("meta/project")
        labels = []
        for label in project.findall("labels/label"):
            attributes = [
                Attribute(**attr.attrib)
                for attr in label.findall("attributes/attribute")
                if len(attr.keys()) >= 1
            ]
            label_data = Label(
                name=label.find("name").text,
                color=label.find("color").text,
                type=label.find("type").text,
                attributes=attributes,
            )
            labels.append(label_data)

        project_data = Project(
            id=project.find("id").text,
            name=project.find("name").text,
            created=project.find("created").text,
            updated=project.find("updated").text,
            labels=labels,
        )

        # Parse tasks
        tasks = []
        for task in project.findall("tasks/task"):
            task_id = task.find("id").text
            url_tag = task.find("segments/segment/url")
            if url_tag is not None:
                task_instance = Task(task_id=task_id, url=url_tag.text)
                tasks.append(task_instance)  # Store the task instance

        # Parse image annotations
        images = []
        for image in root.findall("image"):
            boxes = []
            for box in image.findall("box"):
                box_attributes = [
                    Attribute(name=attr.get("name"), value=attr.text)
                    for attr in box.findall("attribute")
                ]
                boxes.append(Box(**box.attrib, attributes=box_attributes))

            polygons = []
            for polygon in image.findall("polygon"):
                polygon_attributes = [
                    Attribute(name=attr.get("name"), value=attr.text)
                    for attr in polygon.findall("attribute")
                ]
                polygons.append(Polygon(**polygon.attrib, attributes=polygon_attributes))

            masks = []
            for mask in image.findall("mask"):
                mask_attributes = [
                    Attribute(name=attr.get("name"), value=attr.text)
                    for attr in mask.findall("attribute")
                ]
                masks.append(Mask(**mask.attrib, attributes=mask_attributes))

            polylines = []
            for polyline in image.findall("polyline"):
                polyline_attributes = [
                    Attribute(name=attr.get("name"), value=attr.text)
                    for attr in polyline.findall("attribute")
                ]
                polylines.append(
                    Polyline(**polyline.attrib, attributes=polyline_attributes)
                )

            images.append(
                ImageAnnotation(
                    id=image.get("id"),
                    name=image.get("name"),
                    subset=image.get("subset"),
                    task_id=image.get("task_id"),
                    width=int(image.get("width")),
                    height=int(image.get("height")),
                    boxes=boxes,
                    polygons=polygons,
                    masks=masks,
                    polylines=polylines,
                )
            )

        return cls(
            version=root.find("version").text,
            project=project_data,
            images=images,
            tasks=tasks,
        )

    def create_cvat_link(self, image_name: str) -> str:
        """
        Create a CVAT link for the given image name.

        :param image_name: Name of the image.
        :return: A CVAT link. E.g. https://app.cvat.ai/tasks/453747/jobs/520016
        """
        images = list(sorted(self.images, key=lambda image: image.name))
        
        # lookup task id for the given image name
        task_id = None
        for image in images:
            if Path(image.name).name == image_name:
                task_id = image.task_id
                image_id = image.id
                break
        if task_id is None:
            raise ValueError(f"Could not find task ID for image: {image_name}")

        frame_index = 0
        for image in images:
            if image.task_id == task_id:
                if Path(image.name).name == image_name:
                    break

                frame_index += 1

        # lookup job id for the given task id
        job_id = None
        for task in self.tasks:
            if task.task_id == task_id:
                job_id = task.job_id()
                break
        if job_id is None:
            raise ValueError(f"Could not find job ID for task ID: {task_id}")

        return f"https://app.cvat.ai/tasks/{task_id}/jobs/{job_id}?frame={frame_index}"
