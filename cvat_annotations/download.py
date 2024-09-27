import tempfile
import zipfile

from cvat_sdk import Client, make_client
from pydantic_settings import BaseSettings


class CVATConfig(BaseSettings):
    username: str
    password: str

    class Config:
        env_prefix = "CVAT_"
        env_file = ".env.cvat.secrets"


def download(project_id, dataset_path):
    cvat = CVATConfig()

    print(f"Downloading project {project_id} to {dataset_path}")
    with make_client(
        host="app.cvat.ai", credentials=(cvat.username, cvat.password)
    ) as client:
        client: Client

        project = client.projects.retrieve(project_id)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = f"{temp_dir}/dataset.zip"
            project.export_dataset(
                format_name="CVAT for images 1.1",
                filename=temp_file_path,
                include_images=True,
            )

            with zipfile.ZipFile(temp_file_path, "r") as zip_ref:
                zip_ref.extractall(dataset_path)
