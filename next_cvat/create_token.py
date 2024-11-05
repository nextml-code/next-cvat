import base64
import json

from cvat_sdk import make_client


def create_token(username: str, password: str) -> str:
    with make_client(host="app.cvat.ai") as client:
        client.login((username, password))

        token_data = dict(
            sessionid=client.api_client.cookies["sessionid"],
            csrftoken=client.api_client.cookies["csrftoken"],
            api_key=client.api_client.default_headers["Authorization"],
        )
        encoded_token_data = base64.b64encode(json.dumps(token_data).encode()).decode()

        sessionid_expiry = client.api_client.cookies["sessionid"]["expires"]

        print(f"Your machine token is:\n{encoded_token_data}\n")
        print(f"It expires at {sessionid_expiry}.")


def test_create_token():
    from pydantic_settings import BaseSettings

    class Settings(
        BaseSettings, env_prefix="CVAT_", env_file=".env.cvat.secrets", extra="ignore"
    ):
        username: str
        password: str

    settings = Settings()

    create_token(username=settings.username, password=settings.password)
