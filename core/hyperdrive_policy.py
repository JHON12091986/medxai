import logging
from core.config import load_config
from core.task_classifier import ClassifiedTask

logger = logging.getLogger("nina.hyperdrive.policy")

class HyperDrivePolicy:
    """Manages the model strategy, kill-switches, and cost boundaries."""
    
    def __init__(self) -> None:
        self.config = load_config()

    def is_enabled(self) -> bool:
        """Fast-pass check to verify if HyperDrive is enabled in the configuration."""
        try:
            self.config = load_config()
            return getattr(self.config, "hyperdrive_enabled", True)
        except Exception as e:
            logger.error(f"hyperdrive: policy_enabled_check_failed {e}")
            return True

    def estimate_required_tier(self, task: ClassifiedTask) -> str:
        """Decides the optimal execution tier on a cost-to-performance curve."""
        if not self.is_enabled():
            return "DEFAULT"
            
        complexity = task.complexity
        if not isinstance(complexity, str):
            return "DEFAULT"

        complexity = complexity.upper()

        # AST-Guided Dynamic Escalation: escalate if modified files have high risk score (>= 60)
        try:
            import subprocess
            from tools.predictive_ast import analyze_file_risk
            res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            if res.returncode == 0:
                high_risk = False
                for line in res.stdout.splitlines():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        filepath = parts[-1]
                        if filepath.endswith(".py"):
                            risk_data = analyze_file_risk(filepath)
                            if risk_data.get("risk_score", 0) >= 60:
                                high_risk = True
                                break
                if high_risk:
                    logger.info("hyperdrive: Static risk score high (>= 60). Escalating routing tier to LARGE.")
                    return "LARGE"
        except Exception as e:
            logger.debug(f"hyperdrive: failed AST check escalation: {e}")

        if complexity == "SIMPLE":
            return "LOCALFAST"
        elif complexity == "MEDIUM":
            return "FAST"
        elif complexity == "COMPLEX":
            return "DEEP"
        elif complexity == "MASSIVE":
            return "LARGE"
        return "FAST"

    def is_cacheable(self, prompt: str, task: ClassifiedTask) -> bool:
        """Determines if a task's output should be cached based on determinism."""
        if not self.is_enabled():
            return False
            
        # Do not cache interactive chat, reminders, or financial commands
        non_cacheable_triggers = ["remind", "remember", "forget", "buy", "sell", "portfolio", "send mail"]
        prompt_lower = prompt.lower()
        if any(trigger in prompt_lower for trigger in non_cacheable_triggers):
            return False
            
        # Cache standard file lookups, system info, git analysis, and static queries
        cacheable_task_types = ["coding", "system", "search", "default"]
        return task.task_type in cacheable_task_types

# Global singleton
policy = HyperDrivePolicy()
