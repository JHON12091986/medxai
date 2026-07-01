import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List

class ConversationalCritiqueLoop:
    def __init__(self, coder_func: Callable[[str, List[Dict[str, str]]], Any], max_turns: int = 3) -> None:
        self.coder_func = coder_func
        self.max_turns = max_turns

    def verify_code(self, code: str) -> Dict[str, Any]:
        """
        Syntactically checks Python code using py_compile.
        """
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            # Run py_compile
            res = subprocess.run(
                ["python3", "-m", "py_compile", tmp_path],
                capture_output=True,
                text=True,
                check=False
            )
            if res.returncode != 0:
                return {"passed": False, "error": res.stderr or res.stdout}
            return {"passed": True, "error": None}
        finally:
            try:
                Path(tmp_path).unlink()
            except OSError:
                pass

    async def execute_correction_loop(self, initial_prompt: str, initial_code: str) -> Dict[str, Any]:
        """
        Executes the multi-turn coder-verifier conversational loop.
        """
        chat_history = []
        current_code = initial_code
        
        for turn in range(self.max_turns):
            check_result = self.verify_code(current_code)
            if check_result["passed"]:
                return {
                    "success": True,
                    "code": current_code,
                    "turns_taken": turn,
                    "chat_history": chat_history
                }
            
            # The feedback represents the Critic's message
            feedback = f"Verification failed:\n{check_result['error']}\nPlease fix the syntax error."
            chat_history.append({"role": "critic", "content": feedback})
            
            # Call coder function (representing the Executor) to repair
            if asyncio.iscoroutinefunction(self.coder_func):
                current_code = await self.coder_func(feedback, chat_history)
            else:
                current_code = self.coder_func(feedback, chat_history)
            chat_history.append({"role": "coder", "content": current_code})

        # Final check
        final_check = self.verify_code(current_code)
        return {
            "success": final_check["passed"],
            "code": current_code,
            "turns_taken": self.max_turns,
            "chat_history": chat_history,
            "error": final_check["error"]
        }

