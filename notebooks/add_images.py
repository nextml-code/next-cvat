# %%
from cvat_sdk.api_client import models
from PIL import Image

import next_cvat

client = next_cvat.Client.from_env_file(".env.cvat.secrets")


project_id = 198488
job_id = 1442235
task_id = 999670



client.project(project_id).task(task_id)
# %%

cvat = client.project(project_id).labels(name="Deformation")[0]

cvat
# %%

client.project(project_id).tasks()

# %%

client.project(project_id).task(task_id).job(job_id).annotations().add_mask_(

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
