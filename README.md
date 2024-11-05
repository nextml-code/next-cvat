# next-cvat

Downloads and decodes annotations on the format "CVAT for images 1.1".

## Usage

### Create a token

Interactively creates a token if you want to avoid using your username and password:

```bash
cvat create-token
```

_Note that the token expires in 14 days._

### Download dataset

```python
import next_cvat

if __name__ == "__main__":
    next_cvat.Client.from_env_file(".env.cvat.secrets").download_(
        project_id="project-id",
        dataset_path="dataset-path",
    )
```

or using CLI:

```bash
cvat download --project-id <project-id> --dataset-path <dataset-path>
```

### Load annotations

Create a secrets file .env.cvat.secrets:

```bash
CVAT_USERNAME=username
CVAT_PASSWORD=password
```

alternatively, you can use a token:

```bash
CVAT_TOKEN=token
```

And then load annotations:

```python
from next_cvat import Annotations

annotations = Annotations.from_path("path/to/annotations.xml")
```

### Low-level API

```python
from next_cvat import Client

client = Client.from_env_file(".env.cvat.secrets")

with client.cvat_client() as cvat_client:
    cvat_client.get_tasks()
```
