# next-cvat

A Python library for interacting with CVAT (Computer Vision Annotation Tool).

## Installation

```bash
pip install next-cvat
```

## Quick Start

```python
from next_cvat import Client

# Initialize client from environment variables
client = Client.from_env_file(".env.cvat.secrets")

# Get a project
project = client.project(217969)

# Download project data
project.download_("dataset/")

# Load annotations
from next_cvat import Annotations
annotations = Annotations.from_path("dataset/annotations.xml")
```

## Features

- Easy-to-use Python interface for CVAT
- Support for projects, tasks, jobs, and annotations
- Download and upload functionality
- Mask annotation support
- Job status tracking
- Comprehensive type hints and documentation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
