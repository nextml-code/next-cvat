# next-cvat

## Description

Downloads and decodes annotations on format CVAT for images 1.1

## Usage

### Create a token

Interactively creates a token if you want to avoid using your username and password:

```bash
cvat create-token
```

_Note that the token expires in 14 days._

### Download dataset

```python
from next_cvat.download import download

if __name__ == "__main__":
    download(project_id="project-id", dataset_path="dataset-path")
```

or using CLI:

```bash
next_cvat download --project-id <project-id> --dataset-path <dataset-path>
```

### Load annotations

Create a secrets file .env.cvat.secrets:

```bash
CVAT_USERNAME = "username"
CVAT_PASSWORD = "password"
```

And then load annotations:

```python
from next_cvat import Annotations

annotations = Annotations.from_path("path/to/annotations.xml")
```
