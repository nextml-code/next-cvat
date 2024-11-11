# %%
from pathlib import Path

from PIL import Image

import next_cvat

client = next_cvat.Client.from_env_file(".env.cvat.secrets")

client.list_projects()
# %%

# 198488?page=1

project = client.list_projects()[0].fetch()
# %%

client.project(198488).get_tasks()
# %%


# %%
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
    # print(cvat_client.tasks.list())

    # task = cvat_client.tasks.retrieve(999670)

    job = cvat_client.jobs.retrieve(1442235)
    # print(job.get_annotations())

    # job.import_annotations
    # job.set_annotations
    # job.get_annotations
    # job.remove_annotations
    # job.update_annotations

    # print(job.get_annotations())

    annotations = job.get_annotations()

    # print("get_labels", job.get_labels())

    annotations.tracks

    new_mask = next_cvat.Mask.from_segmentation(
        label="Deformation",
        source="automatic",
        occluded=0,
        z_order=0,
        segmentation=Image.open("tests/test_vegetation_mask.png"),
        attributes=[],
    )

    shape = new_mask.shape(
        frame=0,
        label_id=3683899,  # 3683899
        group=0,
    )

    # annotations.shapes.append(shape)

    from cvat_sdk.api_client import models

    # models.LabeledDataRequest

    # request = models.LabeledDataRequest()
    # request.shapes = [shape]

    # job.set_annotations(request)
    # ApiTypeError: Invalid type for variable 'job_annotations_update_request'. Required value type is one of [AnnotationFileRequest, JobAnnotationsUpdateRequest, LabeledDataRequest] and passed type was AnnotationsRead at ['job_annotations_update_request']

    # this uploads images to the task
    # task.upload_data()


    # task = cvat_client.tasks.retrieve(999670)
    # task.import_annotations("CVAT 1.1", "new_annotations.xml")

    # def import_annotations(
    #     self,
    #     format_name: str,
    #     filename: StrPath,
    #     *,
    #     status_check_period: Optional[int] = None,
    #     pbar: Optional[ProgressReporter] = None,
    # ):
# %%
import json

Path("tests/mask_annotations_shapes.json").write_text(
    json.dumps(annotations.shapes[0].to_dict())
)

# %%

shape
# %%
from cvat_sdk.api_client import models

models.LabeledDataRequest
# %%

annotations
# %%

annotations.shapes[1]
# %%

shape
# %%


# %%


# task_id: 999670
client.tasks[task_id].upload_annotations([image_annotation])


# %%

client.list_projects
# %%
