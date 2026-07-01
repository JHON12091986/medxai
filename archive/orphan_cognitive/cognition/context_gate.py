"""Context gate — when a conversation context exceeds 6000 tokens, auto-summarizes the oldest 50% using the injected model callable and replaces those messages with the summary. Prevents context window overflow and reduces cloud token spend."""

import logging
import re
import typing

_ = (re, typing)

GATE_TOKEN_THRESHOLD: int = 6000  # Trigger summarization when estimated token count exceeds this.
SUMMARIZE_OLDEST_FRACTION: float = 0.5  # Fraction of oldest messages to summarize when gate triggers.


def estimate_tokens(messages: list[dict]) -> int:
    """Estimate total token count of a messages list. Uses len(str(messages)) // 4 heuristic."""
    return len(str(messages)) // 4


async def summarize_messages(messages: list[dict], model_fn) -> str:
    """Summarize a list of messages into a compact paragraph using model_fn. model_fn is async callable: async (prompt: str) -> str."""
    text_block = '\n'.join(f'{m["role"].upper()}: {str(m.get("content", ""))[:300]}' for m in messages)
    prompt = f'[NINA CONTEXT GATE] Please summarize the following conversation history into a single compact paragraph:\n{text_block}'
    summary = await model_fn(prompt)
    return summary.strip()


async def process_context_gate(messages: list[dict], model_fn) -> list[dict]:
    """Check token count using estimate_tokens. If < GATE_TOKEN_THRESHOLD, return messages as-is. Identify messages to summarize: keep the system message at the top (if present), then select the oldest 50% of remaining messages. Call summarize_messages on the selected segment. Reconstruct messages: System message (if any) + one assistant summary message ({"role": "assistant", "content": f"[NINA CONTEXT SUMMARY]: {summary}"}) + the remaining unsummarized messages."""
    if estimate_tokens(messages) < GATE_TOKEN_THRESHOLD:
        return messages

    # Deep-ish copy messages to avoid mutating original
    copied_messages = [dict(m) for m in messages]

    system_message = None
    if copied_messages and copied_messages[0].get('role') == 'system':
        system_message = copied_messages[0]
        remaining = copied_messages[1:]
    else:
        remaining = copied_messages

    if not remaining:
        return messages

    num_to_summarize = int(len(remaining) * SUMMARIZE_OLDEST_FRACTION)
    if num_to_summarize <= 0:
        num_to_summarize = 1

    to_summarize = remaining[:num_to_summarize]
    to_keep = remaining[num_to_summarize:]

    logging.info(f"[context_gate] Summarizing oldest {len(to_summarize)} messages of {len(remaining)} total non-system messages")
    summary = await summarize_messages(to_summarize, model_fn)

    summary_message = {
        "role": "assistant",
        "content": f"[NINA CONTEXT SUMMARY]: {summary}"
    }

    result = []
    if system_message:
        result.append(system_message)
    result.append(summary_message)
    result.extend(to_keep)

    return result
