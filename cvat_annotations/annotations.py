from __future__ import annotations

from xml.etree import ElementTree

from .annotation_types import (
    Task,
    Label,
    Project,
    Attribute,
    Box,
    Polygon,
    Mask,
    ImageAnnotation,
    Annotations,
)


def annotations(xml_annotation_path) -> Annotations:
    tree = ElementTree.parse(xml_annotation_path)
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
            )
        )

    # Create the Annotations Pydantic model
    annotations = Annotations(
        version=root.find("version").text,
        project=project_data,
        images=images,
        tasks=tasks,
    )

    return annotations
