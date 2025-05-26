from pathlib import Path

import pytest

import next_cvat


def test_add_tag():
    if not Path(".env.cvat.secrets").exists():
        pytest.skip("No secrets file found")

    client = next_cvat.Client.from_env_file(".env.cvat.secrets")

    project_id = 198488  # Using the same test project as in other tests
    job_id = 1442235
    task_id = 999670
    deformation_attribute_id = 1389238

    job = client.project(project_id).task(task_id).job(job_id)

    annotations = job.annotations()

    annotations.add_tag_(
        next_cvat.Tag(
            label="Deformation",
            source="manual",
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

    print("Successfully added tag annotation")
