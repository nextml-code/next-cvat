from pathlib import Path

import numpy as np
import pytest

import next_cvat


def test_add_polyline():
    if not Path(".env.cvat.secrets").exists():
        pytest.skip("No secrets file found")

    client = next_cvat.Client.from_env_file(".env.cvat.secrets")

    project_id = 198488  # Using the same test project as in test_add_mask
    job_id = 1442235
    task_id = 999670
    deformation_attribute_id = 1389238

    job = client.project(project_id).task(task_id).job(job_id)

    annotations = job.annotations()

    # Create a simple polyline (e.g., a zigzag pattern)
    points = np.array(
        [
            [100, 100],
            [200, 150],
            [300, 100],
            [400, 150],
        ]
    ).tolist()

    annotations.add_polyline_(
        next_cvat.Polyline(
            points=points,
            label="Deformation",
            source="manual",
            occluded=False,
            z_order=0,
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

    print("Successfully added polyline annotation")
