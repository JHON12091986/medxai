import re
from agents.base import AgentMessage, BaseAgent
from core.router import HybridRouter
from core.task_classifier import ClassifiedTask

_HALLUCINATION_RE = re.compile(r"i am a large language model|as an ai|i cannot fulfill this request", re.IGNORECASE)

class CriticAgent(BaseAgent):
    def __init__(self, router: HybridRouter):
        self.router = router

    async def process(self, msg: AgentMessage) -> AgentMessage:
        content = msg.payload.get("content", "")
        task_type = msg.payload.get("task_type", "general")

        is_valid = True
        reason = ""

        if task_type == "research" and len(content) < 100:
            is_valid = False
            reason = "Response too short for a research task."
        elif _HALLUCINATION_RE.search(content):
            is_valid = False
            reason = "AI refusal or boilerplate detected."
        elif task_type in ["coding", "research", "diagnostic"]:
            try:
                task = ClassifiedTask("quick", 100, False, False)
                messages = [
                    {"role": "system", "content": "You are a logic gate. Review this AI response. Check: (1) Is it technically sound and complete? (2) Does it cite a specific file, git command, or tool result as evidence — or does it theorize without reading source? Respond only with 'VALID' or a one-sentence error reason starting with the failed check number."},
                    {"role": "user", "content": f"TASK: {task_type}\nRESPONSE: {content[:2000]}"}
                ]
                _val_pid = "GROQ" if ("GROQ" in self.router.health and self.router.health["GROQ"].cb.can_attempt()) else "LOCALFAST"
                val_content, _, _, _ = await self.router._call_provider(_val_pid, messages, task)
                if "valid" not in val_content.lower():
                    is_valid = False
                    reason = f"Logic Gate Refusal: {val_content}"
            except Exception:
                pass # Fail open on critic failure

        confidence = 1.0 if is_valid else 0.5

        # Send work back to reasoner if invalid, else finish
        recipient = "orchestrator" if is_valid else "reasoner"

        return AgentMessage(
            sender="critic",
            recipient=recipient,
            intent="result",
            payload={
                "valid": is_valid,
                "reason": reason,
                "content": content,
                "goal": msg.payload.get("goal", ""),
                "messages": msg.payload.get("messages", []) + [{"role": "assistant", "content": content}, {"role": "user", "content": f"The previous response failed validation: {reason}. Please refine and provide a correct answer."}] if not is_valid else msg.payload.get("messages", [])
            },
            confidence=confidence,
            inference_cost=0
        )
