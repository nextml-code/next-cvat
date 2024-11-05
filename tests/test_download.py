import tempfile

import next_cvat


def test_download():
    with tempfile.TemporaryDirectory() as temp_dir:
        next_cvat.Client.from_env_file(".env.cvat.secrets").download_(
            project_id=188733,
            dataset_path=temp_dir,
        )
