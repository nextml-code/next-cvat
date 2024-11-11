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
                polygons.append(
                    Polygon(**polygon.attrib, attributes=polygon_attributes)
                )

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

    def save_xml_(self, path: Union[str, Path]) -> Annotations:
        """
        Save annotations to XML file in CVAT format.

        Args:
            path: Path where to save the XML file
        """
        root = ElementTree.Element("annotations")

        # Add version
        version = ElementTree.SubElement(root, "version")
        version.text = self.version

        # Add meta section with project info
        meta = ElementTree.SubElement(root, "meta")
        project = ElementTree.SubElement(meta, "project")

        # Project details
        project_id = ElementTree.SubElement(project, "id")
        project_id.text = self.project.id

        project_name = ElementTree.SubElement(project, "name")
        project_name.text = self.project.name

        created = ElementTree.SubElement(project, "created")
        created.text = self.project.created

        updated = ElementTree.SubElement(project, "updated")
        updated.text = self.project.updated

        # Add labels
        labels_elem = ElementTree.SubElement(project, "labels")
        for label in self.project.labels:
            label_elem = ElementTree.SubElement(labels_elem, "label")

            name = ElementTree.SubElement(label_elem, "name")
            name.text = label.name

            color = ElementTree.SubElement(label_elem, "color")
            color.text = label.color

            type_elem = ElementTree.SubElement(label_elem, "type")
            type_elem.text = label.type

            if label.attributes:
                attrs_elem = ElementTree.SubElement(label_elem, "attributes")
                for attr in label.attributes:
                    attr_elem = ElementTree.SubElement(attrs_elem, "attribute")
                    for key, value in attr.model_dump().items():
                        if value is not None:
                            attr_elem.set(key, str(value))

        # Add tasks
        if self.tasks:
            tasks_elem = ElementTree.SubElement(project, "tasks")
            for task in self.tasks:
                task_elem = ElementTree.SubElement(tasks_elem, "task")
                task_id = ElementTree.SubElement(task_elem, "id")
                task_id.text = task.task_id

                segments = ElementTree.SubElement(task_elem, "segments")
                segment = ElementTree.SubElement(segments, "segment")
                if task.url:
                    url = ElementTree.SubElement(segment, "url")
                    url.text = task.url

        # Add image annotations
        for image in self.images:
            image_elem = ElementTree.Element("image")
            image_elem.set("id", image.id)
            image_elem.set("name", image.name)
            if image.subset:
                image_elem.set("subset", image.subset)
            if image.task_id:
                image_elem.set("task_id", image.task_id)
            image_elem.set("width", str(image.width))
            image_elem.set("height", str(image.height))

            # Add boxes
            for box in image.boxes:
                box_elem = ElementTree.SubElement(image_elem, "box")
                for key, value in box.model_dump().items():
                    if key != "attributes" and value is not None:
                        box_elem.set(key, str(value))

                if box.attributes:
                    for attr in box.attributes:
                        attr_elem = ElementTree.SubElement(box_elem, "attribute")
                        attr_elem.set("name", attr.name)
                        attr_elem.text = attr.value

            # Add polygons
            for polygon in image.polygons:
                poly_elem = ElementTree.SubElement(image_elem, "polygon")
                for key, value in polygon.model_dump().items():
                    if key != "attributes" and value is not None:
                        poly_elem.set(key, str(value))

                if polygon.attributes:
                    for attr in polygon.attributes:
                        attr_elem = ElementTree.SubElement(poly_elem, "attribute")
                        attr_elem.set("name", attr.name)
                        attr_elem.text = attr.value

            # Add masks
            for mask in image.masks:
                mask_elem = ElementTree.SubElement(image_elem, "mask")
                for key, value in mask.model_dump().items():
                    if key != "attributes" and value is not None:
                        mask_elem.set(key, str(value))

                if mask.attributes:
                    for attr in mask.attributes:
                        attr_elem = ElementTree.SubElement(mask_elem, "attribute")
                        attr_elem.set("name", attr.name)
                        attr_elem.text = attr.value

            # Add polylines
            for polyline in image.polylines:
                line_elem = ElementTree.SubElement(image_elem, "polyline")
                for key, value in polyline.model_dump().items():
                    if key != "attributes" and value is not None:
                        line_elem.set(key, str(value))

                if polyline.attributes:
                    for attr in polyline.attributes:
                        attr_elem = ElementTree.SubElement(line_elem, "attribute")
                        attr_elem.set("name", attr.name)
                        attr_elem.text = attr.value

            root.append(image_elem)

        # Create XML tree and save to file
        tree = ElementTree.ElementTree(root)
        tree.write(str(path), encoding="utf-8", xml_declaration=True)

        return self
