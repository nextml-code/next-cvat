from cvat_sdk import make_client
from pydantic_settings import BaseSettings

from .access_token import AccessToken


def create_token(username: str, password: str) -> str:
    with make_client(host="app.cvat.ai") as client:
        client.login((username, password))

        token = AccessToken.from_client_cookies(
            cookies=client.api_client.cookies,
            headers=client.api_client.default_headers,
        )

        encoded_token = token.serialize()
        print(f"Your machine token is:\n{encoded_token}\n")
        print(f"It expires at {token.expires_at}.")

        return encoded_token


def test_create_token():
    class Settings(BaseSettings):
        username: str
        password: str

        class Config:
            env_prefix = "CVAT_"
            env_file = ".env.cvat.secrets"

    settings = Settings()
    create_token(username=settings.username, password=settings.password)
