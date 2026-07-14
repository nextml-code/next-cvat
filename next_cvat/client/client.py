from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Generator

from cvat_sdk import Client as CVATClient
from cvat_sdk import make_client
from pydantic import BaseModel, field_validator

from next_cvat.access_token import AccessToken
from next_cvat.settings import settings

from .frame import Frame
from .job import Job
from .job_annotations import JobAnnotations
from .project import Project
from .task import Task

#: Default CVAT server. Override via the ``CVAT_HOST`` environment variable
#: (e.g. ``CVAT_HOST=https://cvat.nextml.com``) or the ``host=`` argument.
DEFAULT_CVAT_HOST = "https://app.cvat.ai"


class Client(BaseModel):
    username: str | None = None
    password: str | None = None
    token: str | None = None
    host: str = DEFAULT_CVAT_HOST

    @field_validator("host", mode="before")
    @classmethod
    def _normalize_host(cls, value: str | None) -> str:
        """Default empty hosts and ensure an explicit scheme is present.

        Passing a scheme (``https://`` / ``http://``) lets the CVAT SDK skip its
        flaky HTTPS/HTTP auto-detection, which otherwise times out and raises
        ``InvalidHostException`` when the server is slow to answer.
        """
        if value is None or value == "":
            return DEFAULT_CVAT_HOST
        value = value.rstrip("/")
        if not value.startswith(("http://", "https://")):
            value = f"https://{value}"
        return value

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

    @contextmanager
    def cvat_client(self) -> Generator[CVATClient, Any, Any]:
        if self.login_method() == "token":
            with self.token_cvat_client() as client:
                yield client
        elif self.login_method() == "basic":
            with self.basic_cvat_client() as client:
                yield client
        else:
            raise ValueError("Unsupported login method")

    @contextmanager
    def basic_cvat_client(self) -> Generator[CVATClient, None, None]:
        with make_client(
            host=self.host, credentials=(self.username, self.password)
        ) as client:
            client.login((self.username, self.password))
            yield client

    @contextmanager
    def token_cvat_client(self) -> Generator[CVATClient, None, None]:
        with make_client(host=self.host) as client:
            token = AccessToken.deserialize(self.token)

            # Only set Authorization header if we have a real API key (not session-based)
            if token.api_key != "session-based-auth":
                client.api_client.set_default_header(
                    "Authorization", f"Token {token.api_key}"
                )

            client.api_client.cookies["sessionid"] = token.sessionid
            client.api_client.cookies["csrftoken"] = token.csrftoken

            yield client

    def create_token(self) -> AccessToken:
        with self.basic_cvat_client() as client:
            token = AccessToken.from_client_cookies(
                cookies=client.api_client.cookies,
                headers=client.api_client.default_headers,
            )
            return token

    def list_projects(self):
        with self.cvat_client() as client:
            return list(client.projects.list())

    def project(self, project_id: int) -> Project:
        return Project(client=self, id=project_id)

    def download_(self, project_id, dataset_path, include_images=True):
        return self.project(project_id=project_id).download_(
            dataset_path=dataset_path, include_images=include_images
        )


Project.model_rebuild()
Task.model_rebuild()
Job.model_rebuild()
JobAnnotations.model_rebuild()
Frame.model_rebuild()
