from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from cvat_sdk import Client as CVATClient
from cvat_sdk import make_client
from pydantic import BaseModel

from next_cvat.access_token import AccessToken
from next_cvat.settings import settings


class Client(BaseModel):
    username: str | None = None
    password: str | None = None
    token: str | None = None

    @classmethod
    def from_env(cls, env_prefix: str | None = None) -> Client:
        return cls(**settings(env_file=None, env_prefix=env_prefix).model_dump())

    @classmethod
    def from_env_file(cls, env_file: str) -> Client:
        return cls(**settings(env_file=env_file).model_dump())

    def login_method(self) -> str:
        if self.token:
            return "token"
        elif self.username and self.password:
            return "basic"
        else:
            raise ValueError("No credentials found")

    def cvat_client(self) -> CVATClient:
        if self.login_method() == "token":
            return self.token_cvat_client()
        elif self.login_method() == "basic":
            return self.basic_cvat_client()
        else:
            raise ValueError("Unsupported login method")

    @contextmanager
    def basic_cvat_client(self) -> Generator[CVATClient, None, None]:
        with make_client(
            host="app.cvat.ai", credentials=(self.username, self.password)
        ) as client:
            yield client

    @contextmanager
    def token_cvat_client(self) -> Generator[CVATClient, None, None]:
        with make_client(host="app.cvat.ai") as client:
            token = AccessToken.deserialize(self.token)

            client.api_client.set_default_header(
                "Authorization", f"Token {token.api_key}"
            )
            client.api_client.cookies["sessionid"] = token.sessionid
            client.api_client.cookies["csrftoken"] = token.csrftoken

            yield client

    def list_projects(self) -> list:  # [Project]:
        with self.cvat_client() as client:
            return list(client.projects.list())

    # def download(self, project_id, dataset_path):
    #     cvat = CVATConfig()

    #     print(f"Downloading project {project_id} to {dataset_path}")
    #     with make_client(
    #         host="app.cvat.ai", credentials=(cvat.username, cvat.password)
    #     ) as client:
    #         client: CVATClient

    #         project = client.projects.retrieve(project_id)

    #         with tempfile.TemporaryDirectory() as temp_dir:
    #             temp_file_path = f"{temp_dir}/dataset.zip"
    #             project.export_dataset(
    #                 format_name="CVAT for images 1.1",
    #                 filename=temp_file_path,
    #                 include_images=True,
    #             )

    #             with zipfile.ZipFile(temp_file_path, "r") as zip_ref:
    #                 zip_ref.extractall(dataset_path)
