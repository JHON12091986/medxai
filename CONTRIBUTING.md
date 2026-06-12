# Contributing to NINA

First off, thank you for considering contributing to NINA. This project represents a shift from "conversational AI" to "autonomous engineering systems." 

## Code of Conduct
We adhere to standard open-source norms. Be respectful, constructive, and prioritize technical integrity over ego.

## The NINA Architecture Rule
NINA is a self-managing agent. **Before opening a PR, consider whether NINA could write the PR herself.** 
The preferred way to contribute is to submit a "Goal Specification" rather than a raw code patch, allowing the agent to implement your feature.

## PR Process (Manual)
If you are submitting a manual code contribution:
1. Ensure your branch passes the Guardian AST Engine (`python3 guardian_engine.py`).
2. Run `python3 tools/update_index.py` to regenerate the repository map if you added or moved files.
3. Ensure the project is successfully tested: `pytest tests/`.
4. Submit the PR targeting the `main` branch. 

## Code Style
- **Python:** Use type hints. We use `vulture` for dead code detection and enforce clean, synchronous looking async wrappers.
- **Tools:** Any new tool must be registered in `core/capabilities.py`.
- **Secrets:** Never hardcode secrets. Always use `os.environ` and document the requirement in `.env.example`.

## Architecture First
Read `ARCHITECTURE.md` before making any cross-module changes. NINA's routing logic (NinaGate) and orchestration cycles depend heavily on tight integration with `core/router.py`. Do not bypass the router.
