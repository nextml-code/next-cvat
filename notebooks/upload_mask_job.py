# %%
from cvat_sdk.api_client import models
from PIL import Image

import next_cvat

client = next_cvat.Client.from_env_file(".env.cvat.secrets")

project_id = 198488
job_id = 1442235

with client.cvat_client() as cvat_client:
    job = cvat_client.jobs.retrieve(job_id)

    annotations = job.get_annotations()

    request = models.LabeledDataRequest()
    request.shapes = [
        next_cvat.Mask.from_segmentation(
            label="Deformation",
            source="automatic",
            occluded=0,
            z_order=0,
            segmentation=Image.open("tests/test_vegetation_mask.png"),
            attributes=[],
        ).request(
            frame=0,
            label_id=3683899,
            group=0,
        )
    ]

    job.set_annotations(request)

# %%
