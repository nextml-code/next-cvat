import io
from pathlib import Path

import pytest
from PIL import Image


def create_test_image():
    """Create a test image in memory."""
    img = Image.new('RGB', (100, 100), 'white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr


def test_delete_frame(cvat_client, tmp_path):
    # Get a test project
    project = cvat_client.project(217969)
    
    # Create a new task
    task = project.create_task_("test_delete_frame")
    
    # Create and save a temporary test image
    test_image = tmp_path / "test_image.jpg"
    img_data = create_test_image()
    test_image.write_bytes(img_data.getvalue())
    
    # Upload the test image
    task.upload_images_(test_image)
    
    # Get the frame ID
    frames = task.frames()
    assert len(frames) == 1
    frame_id = frames[0].id
    
    # Delete the frame
    task.delete_frame_(frame_id)
    
    # Verify frame was deleted
    frames = task.frames()
    assert len(frames) == 0
    
    # Test deleting non-existent frame
    with pytest.raises(ValueError, match="Frame with ID .* not found"):
        task.delete_frame_(999999) 