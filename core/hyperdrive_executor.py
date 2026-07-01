"""NINA HyperDrive — Task Execution & Speculator (Phase 3)."""
import asyncio
import logging
import httpx
from typing import List, Dict, Any, Optional

logger = logging.getLogger("nina.hyperdrive.executor")

class TaskNode:
    def __init__(self, node_id: str, prompt: str, dependencies: List[str]):
        self.node_id = node_id
        self.prompt = prompt
        self.dependencies = dependencies
        self.status = "PENDING"  # PENDING, RUNNING, COMPLETE, FAILED
        self.result: Optional[Any] = None

class TaskDAG:
    def __init__(self, nodes: List[TaskNode]):
        self.nodes = {n.node_id: n for n in nodes}

    def get_executable_nodes(self) -> List[TaskNode]:
        """Returns nodes whose dependencies are fully met and COMPLETE."""
        executable = []
        for node in self.nodes.values():
            if node.status != "PENDING":
                continue
            deps_met = True
            for dep in node.dependencies:
                dep_node = self.nodes.get(dep)
                if not dep_node or dep_node.status != "COMPLETE":
                    deps_met = False
                    break
            if deps_met:
                executable.append(node)
        return executable

class HyperDriveExecutor:
    """Handles parallel agent/DAG executions and local read-only tool speculation."""

    def __init__(self, ollama_host: str = "http://localhost:11434") -> None:
        self.ollama_host = ollama_host

    async def get_lowest_local_model(self) -> str:
        """Dynamically identifies the lowest-tier local model available in the local Ollama instance."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.ollama_host}/api/tags")
                if res.status_code == 200:
                    models = res.json().get("models", [])
                    if models:
                        # Return the first available model, ideally a smaller model if size is listed
                        models_sorted = sorted(models, key=lambda x: x.get("size", 0))
                        return models_sorted[0].get("name", "qwen2.5:0.5b")
        except Exception as e:
            logger.warning(f"hyperdrive: failed to dynamically lookup Ollama models {e}")
        return "qwen2.5:0.5b"  # Default fallback if Ollama isn't responsive

    async def speculate_next_step(self, context_prompt: str) -> Optional[str]:
        """Uses the fastest local model to speculate on the next safe tool command."""
        target_model = await self.get_lowest_local_model()
        logger.info(f"hyperdrive: speculating next step using fast model {target_model}")
        
        system_instructions = (
            "You are a local speculator. Predict the single next safe read-only CLI command "
            "the user is likely to run (e.g., 'git status', 'ls', 'pytest'). Output only the "
            "command line string, or 'NONE' if uncertain. No markdown formatting, no explainers."
        )
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                payload = {
                    "model": target_model,
                    "messages": [
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": context_prompt}
                    ],
                    "stream": False
                }
                res = await client.post(f"{self.ollama_host}/api/chat", json=payload)
                if res.status_code == 200:
                    prediction = res.json().get("message", {}).get("content", "").strip()
                    if prediction and prediction.upper() != "NONE":
                        # Strip backticks if returned
                        prediction = prediction.replace("`", "")
                        logger.info(f"hyperdrive: speculated action -> {prediction}")
                        return prediction
        except Exception as e:
            logger.warning(f"hyperdrive: speculation failed {e}")
        return None

    async def run_dag(self, dag: TaskDAG, executor_coro) -> Dict[str, Any]:
        """Executes independent DAG nodes concurrently using async task pooling."""
        results = {}
        while True:
            nodes = dag.get_executable_nodes()
            if not nodes:
                # Check if we have any running nodes
                running = any(n.status == "RUNNING" for n in dag.nodes.values())
                if not running:
                    break
                await asyncio.sleep(0.1)
                continue

            async def _run_node(node: TaskNode):
                node.status = "RUNNING"
                try:
                    logger.info(f"hyperdrive: starting parallel node {node.node_id}")
                    node.result = await executor_coro(node.prompt)
                    node.status = "COMPLETE"
                    results[node.node_id] = node.result
                except Exception as e:
                    logger.error(f"hyperdrive: parallel node {node.node_id} failed {e}")
                    node.status = "FAILED"

            # Fire them off in parallel
            await asyncio.gather(*[_run_node(n) for n in nodes])
            
        return results

# Global singleton
executor = HyperDriveExecutor()
