import hashlib
import dataclasses
from typing import Literal

PriorityLevel = Literal["P1", "P2", "P3"]
StatusLevel   = Literal["READY", "BACKLOG"]

@dataclasses.dataclass
class GapItem:
    source: str
    raw_text: str
    priority: PriorityLevel = "P3"
    status: StatusLevel  = "BACKLOG"
    gap_id: str          = dataclasses.field(init=False)

    def __post_init__(self):
        seed = f"{self.source}:{self.raw_text}"
        self.gap_id = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
