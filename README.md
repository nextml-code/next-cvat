# next-cvat

Downloads and decodes annotations on the format "CVAT for images 1.1".

## Usage

Either add environment variables to your global environment or create an env file.

```bash
CVAT_USERNAME=username
CVAT_PASSWORD=password
```

If you don't want to use your username and password, you can create a token:

```bash
cvat create-token
```

And use it like this:

```bash
CVAT_TOKEN=token
```

_Note that the token expires in 14 days._

### Download dataset

```python
import next_cvat

if __name__ == "__main__":
    (
        next_cvat.Client.from_env_file(".env.cvat.secrets")
        .project(1234)
        .download_(dataset_path="dataset-path")
    )
```

or using CLI:

```bash
cvat download --project-id <project-id> --dataset-path <dataset-path>
```

### Load annotations

And then load annotations:

```python
from next_cvat import Annotations

annotations = Annotations.from_path("dataset-path/annotations.xml")
```

### Upload images

```python
import next_cvat

client = next_cvat.Client.from_env()
client.create_task_("batch-1", "images")
client.create_job_("batch-1", "images")
```

### Update annotations

```python
from next_cvat import Annotations

annotations = Annotations.from_path("dataset-path/annotations.xml")

client = next_cvat.Client.from_env()
# client.add_mask_(image_path="image-path", mask=next_cvat.Mask(...))

client.image(image_path="image-path").add_mask_(mask=next_cvat.Mask(...))

```

### Low-level API

```python
from next_cvat import Client

client = Client.from_env_file(".env.cvat.secrets")

with client.cvat_client() as cvat_client:
    cvat_client.get_tasks()
```
