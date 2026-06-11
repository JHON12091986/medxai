import argparse
import asyncio
import sys
import os
from dotenv import dotenv_values
from core.config import NinaConfig
from core.router import (
    HybridRouter,
    ClassifiedTask,
    classify_task,
    PROVIDERS_TIER1,
    PROVIDERS_TIER2,
    PROVIDERS_TIER3,
    LOCAL_PROVIDERS,
)
from core.memory import MemorySystem
from core.agent import AgentLoop
from tools import shell, browser, system as systool, jules_api

async def run_cli():
    parser = argparse.ArgumentParser(description="NINA Command Line Interface")
    parser.add_argument("task", nargs="*", help="The task for NINA to execute")
    parser.add_argument("--model", type=str, help="Override model routing")
    args = parser.parse_args()

    # Read task from stdin if not provided as argument and stdin is piped
    if not args.task:
        if not sys.stdin.isatty():
            task_str = sys.stdin.read().strip()
        else:
            task_str = ""
    else:
        task_str = " ".join(args.task)

    if not task_str:
        parser.print_help()
        sys.exit(1)

    # Load environment variables (dotenv and system env)
    env = {**dotenv_values(".env"), **os.environ}

    # Build NinaConfig manually (avoiding the Telegram token check in load_config)
    tok = env.get("TELEGRAMBOTTOKEN", "")
    uid = env.get("AUTHORIZEDUSERID", "")

    config_kwargs = {}
    env_mapping = {
        "ollama_host": "OLLAMAHOST",
        "cerebras_api_key": "CEREBRAS_API_KEY",
        "groq_api_key": "GROQ_API_KEY",
        "gemini_api_key": "GEMINI_API_KEY",
        "mistral_api_key": "MISTRAL_API_KEY",
        "openrouter_api_key": "OPENROUTER_API_KEY",
        "openai_api_key": "OPEN_AI_API_KEY",
        "deepseek_api_key": "DEEPSEEK_API_KEY",
        "perplexity_api_key": "PERPLEXITY_API_KEY",
        "together_api_key": "TOGETHER_API_KEY",
        "cohere_api_key": "COHERE_API_KEY",
        "fireworks_api_key": "FIREWORKS_API_KEY",
        "xai_api_key": "XAI_API_KEY",
        "sambanova_api_key": "SAMBANOVA_API_KEY",
        "hyperbolic_api_key": "HYPERBOLIC_API_KEY",
        "novita_api_key": "NOVITA_API_KEY",
        "one_brain_api_key": "ONEBRAINAPIKEY",
        "one_brain_api_base": "ONEBRAINAPIBASE",
        "api_secret_key": "APISECRETKEY",
        "ews_password": "EWSPASSWORD",
        "ews_username": "EWS_USERNAME",
        "ews_my_email": "EWS_MY_EMAIL",
        "ews_shared_email": "EWS_SHARED_EMAIL",
        "dead_man_ping_url": "DEADMANPINGURL",
    }
    for k, v in env_mapping.items():
        if v in env and env[v]:
            config_kwargs[k] = env[v]

    config = NinaConfig(
        telegram_bot_token=tok,
        authorized_user_id=uid,
        **config_kwargs
    )

    if "IDLE_AUTO_APPROVE" in env:
        config.idle_auto_approve = env["IDLE_AUTO_APPROVE"].lower() == "true"
    if "IDLE_THRESHOLD_MIN" in env:
        config.idle_threshold_min = int(env["IDLE_THRESHOLD_MIN"])
    if "IDLE_REPORT_MIN" in env:
        config.idle_report_min = int(env["IDLE_REPORT_MIN"])

    # Instantiate and initialize HybridRouter
    router = HybridRouter(config)
    await router.initialize()

    # Instantiate and initialize MemorySystem
    memory = MemorySystem()
    await memory.initialize()

    # Apply --model overrides if specified
    if args.model:
        model_upper = args.model.upper()
        all_providers = [*PROVIDERS_TIER1, *PROVIDERS_TIER2, *PROVIDERS_TIER3, *LOCAL_PROVIDERS]
        if model_upper in all_providers:
            # Force router to only use this specific provider
            def custom_ordered_providers(task, force_local=False):
                return [model_upper]
            router._ordered_providers = custom_ordered_providers
        else:
            # Set general model override for all providers
            for p in all_providers:
                config.model_overrides[p] = args.model

    # Build tools dictionary
    tools = {
        "shell": shell,
        "web": __import__("tools.searchtool", fromlist=["run"]),
        "browser": browser,
        "system": systool,
        "jules": jules_api,
    }

    # Helper for task classification using LOCALFAST
    async def local_fast(prompt: str) -> str:
        msgs = [{"role": "user", "content": prompt}]
        task_cls = ClassifiedTask("quick", 300, False, False)
        try:
            text, _, _, _ = await router._call_provider("LOCALFAST", msgs, task_cls)
            return text
        except Exception:
            return ""

    # Session Bridge context load
    memory_path = "data/memory/session_summaries.md"
    try:
        with open(memory_path, 'r') as mf:
            session_summary = mf.read()
            if session_summary.strip():
                print(f"Context loaded from previous session:\n{session_summary.strip()}")
    except FileNotFoundError:
        pass

    try:
        with open("AGENTS.md", 'r') as af:
            agent_ctx = af.read()
    except FileNotFoundError: agent_ctx = ""

    try:
        with open("docs/memory.md", 'r') as dmf:
            doc_ctx = dmf.read()
    except FileNotFoundError: doc_ctx = ""

    if session_summary or agent_ctx or doc_ctx:
        task_str = f"SYSTEM FACT: Review AGENTS.md and memory.\n\n[SESSION SUMMARY]\n{session_summary}\n\n[AGENT CONTEXT]\n{agent_ctx}\n\n[MEMORY CONTEXT]\n{doc_ctx}\n\n{task_str}"

    # Classify the task
    task = await classify_task(task_str, local_fast)

    # Initialize AgentLoop
    agent = AgentLoop(config, router, memory, tools)

    try:
        # Run agent loop with the task
        result = await agent.run(task_str, task, [])
        print(result)
    finally:
        # Session-End Auto-Update Protocol
        try:
            summary_prompt = f"Summarize this session and capture actionable technical debt and routing failures.\nTask: {task_str}\nResult: {result}"
            task_cls = ClassifiedTask("quick", 300, False, False)
            summary_text, _, _, _ = await router._call_provider("LOCALFAST", [{"role":"user", "content": summary_prompt}], task_cls)
            with open(memory_path, "a") as mf:
                mf.write(f"\n## Session Summary\n{summary_text}\n")
        except Exception:
            pass

        # Clean up router connection
        await router.close()

def main():
    try:
        asyncio.run(run_cli())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
