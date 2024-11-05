import next_cvat


def test_create_token():
    token = next_cvat.Client.from_env_file(".env.cvat.secrets").create_token()
