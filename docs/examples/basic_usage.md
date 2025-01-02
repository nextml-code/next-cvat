# Basic Usage

This guide shows you how to get started with Next CVAT.

## Authentication

First, create a `.env.cvat.secrets` file with your CVAT credentials:

```bash
CVAT_HOST=https://app.cvat.ai
CVAT_USERNAME=your_username
CVAT_PASSWORD=your_password
```

Then you can initialize the client:

```python
from next_cvat import Client

# Initialize client from environment variables
client = Client.from_env_file(".env.cvat.secrets")

# Test the connection by getting a project
project = client.project(217969)  # Use our test project
with project.cvat() as cvat_project:
    assert cvat_project.name is not None  # Verify we can access project data
```

## Working with Projects

You can interact with CVAT projects:

```python
from next_cvat import Client

# Initialize client
client = Client.from_env_file(".env.cvat.secrets")

# Get project metadata
project = client.project(217969)
with project.cvat() as cvat_project:
    print(f"Project name: {cvat_project.name}")
    print(f"Created: {cvat_project.created_date}")

# List tasks in the project
tasks = project.tasks()
print(f"Number of tasks: {len(tasks)}")
```

Each code block in this documentation is automatically tested to ensure it works correctly.
