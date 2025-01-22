import tempfile
from pathlib import Path

import pytest

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
    """Test that job status information is correctly loaded and queried."""
    if not Path(".env.cvat.secrets").exists():
        pytest.skip("No .env.cvat.secrets file found")

    # Create a test annotations XML
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<annotations>
  <version>1.1</version>
  <meta>
    <project>
      <id>1</id>
      <name>Test Project</name>
      <created>2024-01-01 12:00:00.000000+00:00</created>
      <updated>2024-01-01 12:00:00.000000+00:00</updated>
      <labels>
        <label>
          <name>Test</name>
          <color>#ff0000</color>
          <type>any</type>
        </label>
      </labels>
    </project>
    <tasks>
      <task>
        <id>1</id>
        <name>Task 1</name>
        <segments>
          <segment>
            <url>https://app.cvat.ai/api/jobs/101</url>
          </segment>
        </segments>
      </task>
      <task>
        <id>2</id>
        <name>Task 2</name>
        <segments>
          <segment>
            <url>https://app.cvat.ai/api/jobs/102</url>
          </segment>
        </segments>
      </task>
    </tasks>
  </meta>
  <image id="1" name="image1.jpg" width="100" height="100" task_id="1" subset="default">
  </image>
  <image id="2" name="image2.jpg" width="100" height="100" task_id="1" subset="default">
  </image>
  <image id="3" name="image3.jpg" width="100" height="100" task_id="2" subset="default">
  </image>
</annotations>"""
    xml_path = tmp_path / "annotations.xml"
    xml_path.write_text(xml_content)

    # Create a test job status JSON
    job_status_content = """[
    {
        "task_id": "1",
        "job_id": 100,
        "task_name": "Test Task",
        "stage": "annotation",
        "state": "completed",
        "assignee": "user1"
    }
]"""
    job_status_path = tmp_path / "job_status.json"
    job_status_path.write_text(job_status_content)

    # Load annotations with job status
    from next_cvat import Annotations

    annotations = Annotations.from_path(xml_path, job_status_path)

    # Test job status was loaded
    assert len(annotations.job_status) == 1
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


def test_create_cvat_link_includes_frame(annotations_with_job_status):
    """Test that create_cvat_link includes the frame parameter to link directly to an image"""
    # Get any image from the annotations
    image = annotations_with_job_status.images[0]

    # Create link for this image
    link = annotations_with_job_status.create_cvat_link(image.name)

    # Link should contain frame parameter
    assert (
        "?frame=" in link
    ), "Link should contain frame parameter to point to specific image"

    # Frame should be 0 for first image in task
    assert link.endswith("?frame=0"), "First image in task should have frame=0"

    # Create link for second image in same task
    second_image = next(
        img
        for img in annotations_with_job_status.images
        if img.task_id == image.task_id and img.name != image.name
    )
    second_link = annotations_with_job_status.create_cvat_link(second_image.name)

    # Frame should be 1 for second image
    assert second_link.endswith("?frame=1"), "Second image in task should have frame=1"


@pytest.fixture
def annotations_with_job_status(tmp_path):
    """Create test annotations with multiple images in the same task and job status"""
    # Create a test annotations XML with multiple images in same task
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
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
                    <name>test</name>
                    <color>#ff0000</color>
                    <type>any</type>
                </label>
            </labels>
        </project>
        <tasks>
            <task>
                <id>1</id>
                <name>Test Task</name>
                <segments>
                    <segment>
                        <url>http://example.com</url>
                    </segment>
                </segments>
            </task>
        </tasks>
    </meta>
    <image id="1" name="image1.jpg" width="100" height="100" task_id="1">
    </image>
    <image id="2" name="image2.jpg" width="100" height="100" task_id="1">
    </image>
</annotations>"""
    xml_path = tmp_path / "annotations.xml"
    xml_path.write_text(xml_content)

    # Create a test job status JSON
    job_status_content = """[
    {
        "task_id": "1",
        "job_id": 100,
        "task_name": "Test Task",
        "stage": "annotation",
        "state": "completed",
        "assignee": "user1"
    }
]"""
    job_status_path = tmp_path / "job_status.json"
    job_status_path.write_text(job_status_content)

    # Load annotations with job status
    from next_cvat import Annotations

    return Annotations.from_path(xml_path, job_status_path)
