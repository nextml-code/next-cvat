import next_cvat


def test_client():
    client = next_cvat.Client.from_env_file(".env.cvat.secrets")
    projects = client.list_projects()
