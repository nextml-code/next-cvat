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

## Overview

The library provides several key components:

### Client

The main entry point for interacting with CVAT. Handles authentication and provides access to projects, tasks, and jobs.

[View Client Documentation →](api/client.md)

### Annotations

Load, save, and query CVAT annotations. Track job status and manage annotation data.

[View Annotations Documentation →](api/annotations.md)

### Types

Rich set of data types for working with CVAT annotations:

- **Box**: Bounding box annotations
- **Polygon**: Polygon annotations with segmentation support
- **Mask**: Efficient binary mask storage with RLE encoding
- **ImageAnnotation**: Container for image annotations
- **JobStatus**: Track annotation progress
- **Label**: Label definitions with attributes
- **Attribute**: Custom annotation attributes

[View Types Documentation →](api/types.md)

### Projects and Tasks

Manage CVAT projects and tasks:

- **Project**: Container for tasks and labels
- **Task**: Unit of work for annotation
- **Job**: Individual annotation assignments

[View Project Documentation →](api/project.md)  
[View Task Documentation →](api/task.md)  
[View Job Documentation →](api/job.md)

## Examples

For detailed usage examples, see the [Examples](examples/basic_usage.md) section.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
