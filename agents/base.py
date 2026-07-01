from dataclasses import dataclass
import time

@dataclass
class AgentMessage:
    sender: str
    recipient: str
    intent: str
    payload: dict
    confidence: float
    inference_cost: int
    ts: float = 0.0

    def __post_init__(self):
        if not self.ts:
            self.ts = time.time()

class BaseAgent:
    async def process(self, msg: AgentMessage) -> AgentMessage:
        raise NotImplementedError
