import tempfile
from pathlib import Path

from next_cvat.annotations import Annotations


def test_read_mask_annotations():
    """Test reading mask annotations from XML file."""
    annotations = Annotations.from_path("tests/mask_annotations.xml")

    # Test project metadata
    assert annotations.version == "1.1"


def test_roundtrip_mask_annotations():
    """Test reading and writing annotations preserves all data."""
    original = Annotations.from_path("tests/mask_annotations.xml")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir) / "test_output.xml"

        # Write and read back
        original.save_xml_(tmp_path)
        reloaded = Annotations.from_path(tmp_path)

    # Compare all fields
    assert original.version == reloaded.version
    assert original.project.model_dump() == reloaded.project.model_dump()
    assert len(original.tasks) == len(reloaded.tasks)
    assert original.tasks[0].model_dump() == reloaded.tasks[0].model_dump()

    # Compare images
    assert len(original.images) == len(reloaded.images)
    orig_image = original.images[0]
    reload_image = reloaded.images[0]

    assert orig_image.id == reload_image.id
    assert orig_image.name == reload_image.name
    assert orig_image.width == reload_image.width
    assert orig_image.height == reload_image.height
    assert orig_image.task_id == reload_image.task_id

    # Compare masks
    assert len(orig_image.masks) == len(reload_image.masks)
    orig_mask = orig_image.masks[0]
    reload_mask = reload_image.masks[0]
    assert orig_mask.model_dump() == reload_mask.model_dump()


def test_job_status(tmp_path):
    """Test loading and using job status information."""
    # Create a test annotations XML
    xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<annotations>
    <version>1.1</version>
    <meta>
        <project>
            <id>123</id>
            <name>Test Project</name>
            <created>2024-01-01 12:00:00</created>
            <updated>2024-01-01 12:00:00</updated>
            <labels>
                <label>
                    <name>Test</name>
                    <color>#ff0000</color>
                    <type>any</type>
                </label>
            </labels>
            <tasks>
                <task>
                    <id>1</id>
                    <segments>
                        <segment>
                            <url>http://example.com</url>
                        </segment>
                    </segments>
                </task>
                <task>
                    <id>2</id>
                    <segments>
                        <segment>
                            <url>http://example.com</url>
                        </segment>
                    </segments>
                </task>
            </tasks>
        </project>
    </meta>
    <image id="1" name="image1.jpg" task_id="1" width="100" height="100" subset="train" />
    <image id="2" name="image2.jpg" task_id="1" width="100" height="100" subset="train" />
    <image id="3" name="image3.jpg" task_id="2" width="100" height="100" subset="train" />
</annotations>'''
    xml_path = tmp_path / "annotations.xml"
    xml_path.write_text(xml_content)

    # Create a test job status JSON
    job_status_content = '''[
    {
        "task_id": "1",
        "job_id": 101,
        "task_name": "Task 1",
        "stage": "annotation",
        "state": "completed",
        "assignee": "user1"
    },
    {
        "task_id": "2",
        "job_id": 102,
        "task_name": "Task 2",
        "stage": "annotation",
        "state": "in_progress",
        "assignee": "user2"
    }
]'''
    job_status_path = tmp_path / "job_status.json"
    job_status_path.write_text(job_status_content)

    # Load annotations with job status
    from next_cvat import Annotations
    annotations = Annotations.from_path(xml_path, job_status_path)

    # Test job status was loaded
    assert len(annotations.job_status) == 2
    assert annotations.job_status[0].task_id == "1"
    assert annotations.job_status[0].state == "completed"

    # Test getting task status
    task1_status = annotations.get_task_status("1")
    assert task1_status == {"101": "completed"}

    # Test getting completed tasks
    completed_tasks = annotations.get_completed_tasks()
    assert len(completed_tasks) == 1
    assert completed_tasks[0].task_id == "1"

    # Test getting completed task IDs
    completed_task_ids = annotations.get_completed_task_ids()
    assert completed_task_ids == ["1"]

    # Test getting images from completed tasks
    completed_images = annotations.get_images_from_completed_tasks()
    assert len(completed_images) == 2
    assert {img.name for img in completed_images} == {"image1.jpg", "image2.jpg"}
