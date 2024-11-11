# %%
from pathlib import Path

from PIL import Image

import next_cvat

client = next_cvat.Client.from_env_file(".env.cvat.secrets")

project_id = 198488

project_export_path = f"test-download-project-{project_id}"
# %%

client.download_(project_id, project_export_path)
# %%

annotations = next_cvat.Annotations.from_path(
    Path(project_export_path) / "annotations.xml"
)

annotations
# %%

new_mask = next_cvat.Mask.from_segmentation(
    label="Deformation",
    source="automatic",
    occluded=0,
    z_order=0,
    segmentation=Image.open("tests/test_vegetation_mask.png"),
    attributes=[],
)
new_mask

annotations.images[0].masks.append(new_mask)

annotations.save_xml_("new_annotations.xml")
# %%

with client.cvat_client() as cvat_client:
    job = cvat_client.jobs.retrieve(1442235)

    task = cvat_client.tasks.retrieve(999670)
    task.import_annotations("CVAT 1.1", "new_annotations.xml")

    # Note: this will duplicate all existing annotations, would need to clear all other shapes

# %%
