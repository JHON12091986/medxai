"""NINA HyperDrive — Context Optimizer (Phase 2)."""
import logging
from typing import List, Dict, Any

logger = logging.getLogger("nina.hyperdrive.context")

# Safelist of elements that must NEVER be stripped during observation masking
MASK_SAFELIST = [
    "exit code", "exit status", "error", "success", "fail", "warning",
    "compile status", "passed", "failed", "exception", "traceback",
    "json", "{", "}"
]

class HyperDriveContextOptimizer:
    """Manages context compression, semantic reranking, and observation masking."""

    def compress_state(self, history: List[Dict[str, Any]], character_budget: int = 12000) -> List[Dict[str, Any]]:
        """Condenses old conversational history into a compressed summary block if budget is exceeded."""
        total_len = sum(len(str(turn.get("content", ""))) for turn in history)
        if total_len <= character_budget or len(history) <= 4:
            return history

        logger.info(f"hyperdrive: context length {total_len} exceeds budget. Compressing history.")
        # Retain the system prompt and the last 2 turns, compress everything in between
        system_prompt = history[0] if history and history[0].get("role") == "system" else None
        last_turns = history[-2:] if len(history) >= 2 else history
        
        middle_turns = history[1:-2] if system_prompt else history[:-2]
        
        # Simple local/structural concatenation or summaries
        summary_content = (
            f"[HyperDrive Context Compression: {len(middle_turns)} turns condensed]\n"
            f"Themes covered previously: " + 
            ", ".join(set(turn.get("role", "") for turn in middle_turns)) + "\n"
        )
        
        summary_turn = {"role": "system", "content": summary_content}
        
        new_history = []
        if system_prompt:
            new_history.append(system_prompt)
        new_history.append(summary_turn)
        new_history.extend(last_turns)
        return new_history

    def rerank_relevance(self, chunks: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Reranks retrieved context chunks using keyword-density and query matching."""
        if not chunks:
            return chunks
            
        query_words = set(query.lower().split())
        if not query_words:
            return chunks

        scored_chunks = []
        for chunk in chunks:
            content = str(chunk.get("content", "")).lower()
            overlap = sum(1 for word in query_words if word in content)
            scored_chunks.append((overlap, chunk))
            
        # Sort descending by query overlap score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored_chunks]

    def mask_observations(self, content: str) -> str:
        """Masks large stdout terminal dumps, keeping only critical safelist info."""
        lines = content.splitlines()
        if len(lines) <= 25:
            return content

        logger.info(f"hyperdrive: masking large output observation ({len(lines)} lines)")
        kept_lines = []
        masked_count = 0
        
        # Keep the first 5 lines of context
        kept_lines.extend(lines[:5])
        
        # Scan middle lines with safelist
        for line in lines[5:-5]:
            line_lower = line.lower()
            if any(safeword in line_lower for safeword in MASK_SAFELIST):
                kept_lines.append(line)
            else:
                masked_count += 1
                
        # Keep the last 5 lines of context
        kept_lines.extend(lines[-5:])
        
        if masked_count > 0:
            kept_lines.insert(5, f"\n... [HyperDrive masked {masked_count} lines of verbose output] ...\n")
            
        return "\n".join(kept_lines)

# Global singleton
optimizer = HyperDriveContextOptimizer()
