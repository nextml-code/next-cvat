# Project

The `Project` class represents a CVAT project containing tasks and labels.

## Properties

- `id: str` - Unique identifier for the project
- `name: str` - Human-readable name of the project
- `created: str` - Timestamp when the project was created
- `updated: str` - Timestamp when the project was last updated
- `labels: List[Label]` - List of label definitions for the project

## Usage

```python
project = Project(
    id="217969",
    name="My Project",
    created="2024-01-01 12:00:00.000000+00:00",
    updated="2024-01-01 12:00:00.000000+00:00",
    labels=[
        Label(name="car", color="#ff0000", type="any"),
        Label(name="person", color="#00ff00", type="any")
    ]
)
```
