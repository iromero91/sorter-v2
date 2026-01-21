from dataclasses import dataclass, field
from typing import Optional
import uuid
import time


@dataclass
class KnownObject:
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    part_id: Optional[str] = None
