from pathlib import Path

import pytest
from PIL import Image

import next_cvat


def test_add_mask():
    if not Path(".env.cvat.secrets").exists():
        pytest.skip("No secrets file found")

    client = next_cvat.Client.from_env_file(".env.cvat.secrets")

    project_id = 198488
    job_id = 1442235
    task_id = 999670
    deformation_attribute_id = 1389238

    job = client.project(project_id).task(task_id).job(job_id)

    annotations = job.annotations()

    annotations.add_mask_(
        next_cvat.Mask.from_segmentation(
            segmentation=Image.open("tests/test_vegetation_mask.png"),
            label="Deformation",
            attributes=[
                next_cvat.Attribute(
                    name="Severity",
                    value="High",
                    spec_id=deformation_attribute_id,
                )
            ],
        ),
        image_name="20240916_000854_2011T_437.bmp",
    )

    job.update_annotations_(annotations)
