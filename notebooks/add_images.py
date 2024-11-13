# %%
from cvat_sdk.api_client import models
from PIL import Image

import next_cvat

client = next_cvat.Client.from_env_file(".env.cvat.secrets")


project_id = 198488
job_id = 1442235
task_id = 999670


# job = client.project(project_id).task(task_id).job(job_id)


client.project(project_id).task(task_id).frames()[0]
# %%



# %%
annotations = job.annotations()


annotations.add_mask_(
    next_cvat.Mask.from_segmentation(
        segmentation=Image.open("tests/test_vegetation_mask.png"),
        label="Deformation",
    ),
    image_name="20240916_000854_2011T_437.bmp",
)

job.update_annotations_(annotations)
# %%


# %%

with client.project(project_id).task(task_id).cvat() as cvat_task:
    print(cvat_task.get_frames_info())
    print(cvat_task)
# %%

with client.project(project_id).cvat() as cvat_project:
    # print(cvat_project.get_labels())
    # print(cvat_project.get_annotations())

    export = cvat_project.export()


# %%


with client.project(project_id).task(task_id).job(job_id).cvat() as cvat_job:
    print(cvat_job)

# %%

cvat = client.project(project_id).labels(name="Deformation")[0]

cvat
# %%

client.project(project_id).tasks()

# %%


# %%

job = client.project(project_id).task(task_id).job(job_id)
# %%

annotations = job.annotations().add_mask_(
    next_cvat.Mask(
        name="Deformation",
        image=Image.open("tests/test_vegetation_mask.png"),
    ),
    image_path="example batch/20230120_122959_2011T_10132714_10134250.png",
)

job.update_annotations_(annotations)
# %%


task = client.project(project_id).task(task_id)
# %%

with task.cvat() as cvat_task:
    print(cvat_task.get_tasks())
# %%

project = client.project(project_id)
# %%

with project.cvat() as cvat_project:
    print(cvat_project.get_tasks())
# %%


cvat.to_dict()
# %%

cvat.id
# %%

with client.cvat_client() as cvat_client:
    tasks = cvat_client.projects.retrieve(project_id)

    # jobs = cvat_client.jobs.list(project_id=project_id)

    # job = cvat_client.jobs.retrieve(job_id)

    # annotations = job.get_annotations()

    project = cvat_client.projects.retrieve(project_id)

    print(project.get_labels())

    task = cvat_client.tasks.retrieve(task_id)

    print(type(task))

# %%

project.get_tasks()
# %%
project.get_labels()
# %%

cvat_client.jobs.retrieve(job_id).set_annotations()
# %%
cvat_client.jobs.retrieve(job_id).get_annotations()


# %%

cvat_client.users.list()
# %%

cvat_client.jobs.list()
# %%

cvat_client.jobs.retrieve
# %%

cvat_client.tasks.retrieve


# %%


task = client.project(project_id).create_task_("batch-1", "images")
# %%

task_id = task.id

client.project(project_id).task(task_id).create_job_("batch-1", "images")
# %%


# %%
