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
