import tempfile
from pathlib import Path
from xml.etree import ElementTree

import pytest

import next_cvat
from next_cvat import Annotations, Attribute, ImageAnnotation, Project, Tag, Task


def test_tag_creation():
    """Test that a tag can be created."""
    tag = Tag(label="no-crack", source="manual", attributes=[])
    assert tag.label == "no-crack"
    assert tag.source == "manual"
    assert tag.attributes == []


def test_tag_with_attributes():
    """Test that a tag can be created with attributes."""
    tag = Tag(
        label="no-crack",
        source="manual",
        attributes=[Attribute(name="confidence", value="0.95")],
    )
    assert tag.label == "no-crack"
    assert tag.source == "manual"
    assert len(tag.attributes) == 1
    assert tag.attributes[0].name == "confidence"
    assert tag.attributes[0].value == "0.95"


def test_load_and_save_tags():
    """Test that tags can be loaded from and saved to XML."""
    # Create test XML with a tag
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
    <annotations>
        <version>1.1</version>
        <meta>
            <project>
                <id>123</id>
                <name>Test Project</name>
                <created>2021-01-01T00:00:00Z</created>
                <updated>2021-01-01T00:00:00Z</updated>
                <labels>
                    <label>
                        <name>crack</name>
                        <color>#ff0000</color>
                        <type>any</type>
                    </label>
                </labels>
            </project>
        </meta>
        <image id="1" name="image1.jpg" task_id="1" width="800" height="600">
            <tag label="no-crack" source="manual">
                <attribute name="confidence">0.95</attribute>
            </tag>
        </image>
    </annotations>
    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        xml_path = Path(tmp_dir) / "annotations.xml"
        with open(xml_path, "w") as f:
            f.write(xml_content)

        # Load annotations
        annotations = Annotations.from_path(xml_path)

        # Check that tag was loaded
        assert len(annotations.images) == 1
        image = annotations.images[0]
        assert len(image.tags) == 1
        tag = image.tags[0]
        assert tag.label == "no-crack"
        assert tag.source == "manual"
        assert len(tag.attributes) == 1
        assert tag.attributes[0].name == "confidence"
        assert tag.attributes[0].value == "0.95"

        # Save annotations
        output_path = Path(tmp_dir) / "output.xml"
        annotations.save_xml_(output_path)

        # Parse saved XML and check tag
        tree = ElementTree.parse(output_path)
        root = tree.getroot()

        image_elem = root.find("image")
        assert image_elem is not None

        tag_elem = image_elem.find("tag")
        assert tag_elem is not None
        assert tag_elem.get("label") == "no-crack"
        assert tag_elem.get("source") == "manual"

        attr_elem = tag_elem.find("attribute")
        assert attr_elem is not None
        assert attr_elem.get("name") == "confidence"
        assert attr_elem.text == "0.95"


def test_add_tag_to_annotations():
    """Test adding a tag to existing annotations."""
    # Create a simple annotations object
    project = Project(
        id="123",
        name="Test Project",
        created="2021-01-01T00:00:00Z",
        updated="2021-01-01T00:00:00Z",
        labels=[],
    )

    image = ImageAnnotation(
        id="1",
        name="image1.jpg",
        width=800,
        height=600,
        task_id="1",
    )

    annotations = Annotations(
        version="1.1",
        project=project,
        tasks=[Task(task_id="1", name="Task 1")],
        images=[image],
    )

    # Add a tag
    tag = Tag(label="no-crack", source="manual", attributes=[])
    annotations.images[0].tags.append(tag)

    # Check that tag was added
    assert len(annotations.images[0].tags) == 1
    assert annotations.images[0].tags[0].label == "no-crack"

    # Save and load annotations
    with tempfile.TemporaryDirectory() as tmp_dir:
        xml_path = Path(tmp_dir) / "annotations.xml"
        annotations.save_xml_(xml_path)

        loaded_annotations = Annotations.from_path(xml_path)

        # Check that tag is still there
        assert len(loaded_annotations.images[0].tags) == 1
        assert loaded_annotations.images[0].tags[0].label == "no-crack"


def test_with_real_example():
    """Test using the example from the annotations.xml file."""
    # Create test XML with the provided example
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
    <annotations>
        <version>1.1</version>
        <meta>
            <project>
                <id>123</id>
                <name>Test Project</name>
                <created>2021-01-01T00:00:00Z</created>
                <updated>2021-01-01T00:00:00Z</updated>
                <labels>
                    <label>
                        <name>crack</name>
                        <color>#ff0000</color>
                        <type>any</type>
                    </label>
                </labels>
            </project>
        </meta>
        <image id="2" name="some_image.png" subset="default" task_id="1387700" width="4096" height="627">
            <tag label="no-crack" source="manual">
            </tag>
        </image>
    </annotations>
    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        xml_path = Path(tmp_dir) / "annotations.xml"
        with open(xml_path, "w") as f:
            f.write(xml_content)

        # Load annotations
        annotations = Annotations.from_path(xml_path)

        # Check that tag was loaded
        assert len(annotations.images) == 1
        image = annotations.images[0]
        assert image.name == "some_image.png"
        assert len(image.tags) == 1
        tag = image.tags[0]
        assert tag.label == "no-crack"
        assert tag.source == "manual"
        assert len(tag.attributes) == 0
