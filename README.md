# next-cvat

## Description

Downloads and decodes annotations on format CVAT for images 1.1

## Usage

Create a secrets file .env.cvat.secrets

```bash
CVAT_USERNAME = "username"
CVAT_PASSWORD = "password"
```

```python
from next_cvat import Annotations

annotations = Annotations.from_path("path/to/annotations.xml")
```
