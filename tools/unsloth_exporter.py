"""
NINA Unsloth Fine-Tuning Data Exporter (LT-5)
Parses interaction logs and converts them into JSON datasets formatted for Unsloth LoRA pipelines.
"""
from __future__ import annotations
import json
import os
import logging
from typing import Dict, List

logger = logging.getLogger("nina.tools.unsloth_exporter")

class UnslothExporter:
    def __init__(self, telemetry_path: str = "telemetry.jsonl", scratch_path: str = "data/gemini_scratch.jsonl") -> None:
        self.telemetry_path = telemetry_path
        self.scratch_path = scratch_path

    def export_to_alpaca(self, output_path: str = "data/unsloth_alpaca_dataset.json") -> bool:
        """
        Formats NINA execution logs into Alpaca JSON schema:
        [ { "instruction": "...", "input": "...", "output": "..." } ]
        """
        logger.info("Starting Alpaca format export for Unsloth pipeline...")
        dataset: List[Dict[str, str]] = []

        # 1. Parse Gemini Scratch/Interaction logs if available
        if os.path.exists(self.scratch_path):
            try:
                with open(self.scratch_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            # Convert search, thinking, or OODA logs to QA pairs
                            if "goal" in data or "prompt" in data:
                                instr = data.get("goal") or data.get("prompt", "")
                                resp = data.get("response") or data.get("result", "")
                                if instr and resp:
                                    dataset.append({
                                        "instruction": "Execute NINA agent cognitive task.",
                                        "input": str(instr),
                                        "output": str(resp)
                                    })
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.warning(f"Error reading scratch path {self.scratch_path}: {e}")

        # 2. Parse Telemetry logs
        if os.path.exists(self.telemetry_path):
            try:
                with open(self.telemetry_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            event = data.get("event")
                            if event == "node_done" or event == "node_start":
                                # Extract structured task OODA loops
                                prompt = data.get("prompt")
                                result = data.get("result")
                                if prompt and result:
                                    dataset.append({
                                        "instruction": f"Solve NINA subtask: {data.get('label', 'unlabeled')}",
                                        "input": str(prompt),
                                        "output": str(result)
                                    })
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.warning(f"Error reading telemetry path {self.telemetry_path}: {e}")

        # De-duplicate entries
        seen = set()
        deduped_dataset = []
        for entry in dataset:
            key = (entry["input"], entry["output"])
            if key not in seen:
                seen.add(key)
                deduped_dataset.append(entry)

        # Write output file
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(deduped_dataset, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully exported {len(deduped_dataset)} dataset rows to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write Unsloth dataset: {e}")
            return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    exporter = UnslothExporter()
    exporter.export_to_alpaca()
