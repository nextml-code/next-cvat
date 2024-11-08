from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw
from pydantic import BaseModel, field_validator


class Task(BaseModel):
    task_id: str
    url: str

    def job_id(self) -> str:
        """
        Extracts the job ID from the given URL.
        Assumes the job ID is the last numeric part of the URL.
        """
        parts = self.url.rstrip("/").split("/")
        for part in reversed(parts):
            if part.isdigit():
                return part
        raise ValueError(f"Could not extract job ID from URL: {self.url}")
