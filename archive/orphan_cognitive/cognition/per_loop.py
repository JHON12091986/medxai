"""Plan-Execute-Reflect (PER) loop — NINA reasons like a senior engineer. For complex queries, generates an internal plan, executes step by step, then scores the result and retries once if confidence is below threshold."""

import asyncio
import dataclasses
import enum
import logging
import time
import typing
import re

_ = asyncio


class PERState(enum.Enum):
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    REFLECTING = "REFLECTING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"

@dataclasses.dataclass
class PERStep:
    step_id: int
    description: str
    result: str = ''
    success: bool = False
    duration_s: float = 0.0

@dataclasses.dataclass
class PERTrace:
    query: str
    plan: list[PERStep]
    final_answer: str = ''
    confidence: float = 0.0
    state: PERState = PERState.PLANNING
    retried: bool = False
    total_duration_s: float = 0.0

CONFIDENCE_THRESHOLD: float = 0.72  # Retry once if reflection scores below this. Tune empirically.

async def run_per_loop(query: str, model_fn: typing.Callable, *, confidence_threshold: float = CONFIDENCE_THRESHOLD, max_plan_steps: int = 5) -> PERTrace:
    """Run the Plan-Execute-Reflect loop for a complex query. model_fn is an async callable: async def model_fn(prompt: str) -> str. Returns a PERTrace with the full reasoning record."""
    t_start = time.monotonic()
    trace = PERTrace(query=query, plan=[])
    trace.state = PERState.PLANNING

    # PLAN PHASE
    plan_prompt = f'[NINA PLAN MODE] Break this query into at most {max_plan_steps} concrete steps. Output ONLY a numbered list of steps, one per line, no preamble:\n{query}'
    plan_response = await model_fn(plan_prompt)
    
    # Parse plan steps
    step_idx = 0
    for line in plan_response.split('\n'):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        # Filter lines that start with a digit or '-'
        if re.match(r'^(\d+|-)', line_stripped):
            # Clean up the step text
            step_text = re.sub(r'^(\d+[\s.:]*|-+\s*)', '', line_stripped).strip()
            if step_text:
                trace.plan.append(PERStep(step_id=step_idx, description=step_text))
                step_idx += 1

    if not trace.plan:
        trace.plan.append(PERStep(step_id=0, description='Direct answer (no decomposition possible)'))

    # EXECUTE PHASE
    trace.state = PERState.EXECUTING
    for step in trace.plan:
        t0 = time.monotonic()
        execute_prompt = f'[NINA EXECUTE STEP {step.step_id}] Query context: {query}\nStep to execute: {step.description}\nProvide a concise result for this step only.'
        result = await model_fn(execute_prompt)
        step.result = result
        step.success = len(result.strip()) > 10 and 'error' not in result.lower()[:50]
        step.duration_s = time.monotonic() - t0

    # REFLECT PHASE
    trace.state = PERState.REFLECTING
    execution_summary = '\n'.join(f'Step {s.step_id}: {s.description}\nResult: {s.result}' for s in trace.plan)
    reflect_prompt = f'[NINA REFLECT] Original query: {query}\nExecution summary:\n{execution_summary}\n\nNow synthesize a final answer. Then on the last line output exactly: CONFIDENCE: <float 0.0-1.0>'
    reflection = await model_fn(reflect_prompt)

    # Parse confidence
    confidence = 0.65
    confidence_lines = reflection.split('\n')
    confidence_line_idx = -1
    for i, line in enumerate(reversed(confidence_lines)):
        m = re.search(r'CONFIDENCE:\s*([0-9.]+)', line, re.IGNORECASE)
        if m:
            try:
                confidence = float(m.group(1))
                confidence_line_idx = len(confidence_lines) - 1 - i
                break
            except ValueError:
                pass

    trace.confidence = confidence

    # Strip the CONFIDENCE line from reflection to get final_answer
    if confidence_line_idx != -1:
        clean_lines = confidence_lines[:confidence_line_idx] + confidence_lines[confidence_line_idx+1:]
        trace.final_answer = '\n'.join(clean_lines).strip()
    else:
        # If confidence line not found, check if it's anywhere in the reflection and remove it
        trace.final_answer = re.sub(r'CONFIDENCE:\s*[0-9.]+', '', reflection, flags=re.IGNORECASE).strip()

    # RETRY
    if trace.confidence < confidence_threshold and not trace.retried:
        trace.retried = True
        retry_prompt = f'[NINA RETRY] Your previous answer had confidence {trace.confidence:.2f}. Retry with more care.\nQuery: {query}\nPrevious answer: {trace.final_answer}'
        retry_result = await model_fn(retry_prompt)
        trace.final_answer = retry_result
        trace.confidence = min(trace.confidence + 0.15, 1.0)

    trace.state = PERState.COMPLETE
    trace.total_duration_s = time.monotonic() - t_start
    logging.info(f'[per_loop] query_len={len(query)} steps={len(trace.plan)} confidence={trace.confidence:.2f} retried={trace.retried} duration={trace.total_duration_s:.2f}s')
    return trace
