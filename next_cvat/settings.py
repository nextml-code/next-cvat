from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    username: Optional[str] = None
    password: Optional[str] = None

    def __init__(self, env_file: Optional[Path] = None):
        env_files = [".env.cvat.secrets"]
        if env_file:
            env_files.insert(0, str(env_file))
        super().__init__(_env_file=env_files, _env_prefix="CVAT_") 