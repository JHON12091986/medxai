# Kimi Agent Swarm Reference

**Kimi Agent Swarm** is a native, self-directed AI architecture developed by Chinese AI lab [Moonshot AI](https://www.moonshot.ai/). Instead of relying on a user to hand-build pipelines, it uses a **model-native master orchestrator** to automatically split a single complex prompt into parallel sub-tasks and deploy dozens to hundreds of specialized sub-agents simultaneously. [[1](https://www.datacamp.com/tutorial/kimi-k2-agent-swarm-guide), [2](https://www.youtube.com/watch?v=F6nUrJ-HDeM), [3](https://www.kimi.com/blog/kimi-k2-5), [4](https://www.youtube.com/watch?v=WuOlqBsDg-w)]

Introduced with Kimi K2.5 and significantly expanded in Kimi K2.6, this paradigm moves away from single-threaded, linear chatbot responses toward large-scale autonomous workforce execution. [[1](https://www.youtube.com/watch?v=GwKoFpUV69M), [2](https://www.datacamp.com/tutorial/kimi-k2-agent-swarm-guide)]

---

## Core Mechanics & Evolution

### Kimi K2.5 Implementation
- **Scale**: Spawns up to **100 sub-agents** working in parallel.
- **Execution Limit**: Capable of executing up to **1,500 tool calls** per prompt.
- **Speed Efficiency**: Completes wide research and data acquisition tasks up to **4.5x faster** than standard single-agent setups. [[1](https://www.datacamp.com/tutorial/kimi-k2-agent-swarm-guide), [2](https://www.kimi.com/blog/kimi-k2-5), [3](https://medium.com/@doubletaken/kimi-k2-5-redefining-ai-workflow-with-agent-swarm-2d50e76a7470)]

### Kimi K2.6 & Kimi Work Upgrade
- **Scale Expansion**: Scaled up to **300 sub-agents** executing simultaneously.
- **Step Budget**: Increased capacity to **4,000 coordinated steps**.
- **Long Horizon Tasks**: Proven to sustain over **13 hours of continuous work** on massive codebases or complex data engineering projects.
- **Document-to-Skill**: Converts PDFs, Word files, and spreadsheets directly into custom toolsets and domain knowledge for individual sub-agents. [[1](https://www.youtube.com/watch?v=F6nUrJ-HDeM), [2](https://www.marktechpost.com/2026/06/12/moonshot-ai-launches-kimi-work-a-local-desktop-agent-reportedly-running-on-kimi-k2-6-with-a-300-sub-agent-agent-swarm/), [3](https://www.verdent.ai/guides/kimi-k2-6-agent-swarm), [4](https://www.kimi.com/blog/kimi-k2-6)]

---

## Key Technical Innovations

- **Parallel Agent Reinforcement Learning (PARL)**: Traditional LLMs suffer from "serial collapse" because they are trained on sequential text generation. Moonshot AI engineered PARL to train the model's output tokens to natively map out and track wide, concurrent graph structures instead of linear outputs. [[1](https://www.youtube.com/watch?v=GwKoFpUV69M), [2](https://www.youtube.com/watch?v=G2MUGP_1ydc)]
- **Dynamic Orchestration**: Users do not need to assign roles like "coder" or "researcher". The master agent evaluates the objective, builds a step-by-step blueprint, names and provisions specialized sub-agents dynamically, and scales them down if a task turns out to be simple. [[1](https://www.datacamp.com/tutorial/kimi-k2-agent-swarm-guide), [2](https://www.youtube.com/watch?v=G2MUGP_1ydc)]
- **WebBridge Integration**: Embedded in desktop toolsets like Kimi Work, sub-agents can share the user's secure browser session to perform live lookups, scroll pages, fill out complex forms, and parse deep web data across multiple tabs. [[1](https://www.marktechpost.com/2026/06/12/moonshot-ai-launches-kimi-work-a-local-desktop-agent-reportedly-running-on-kimi-k2-6-with-a-300-sub-agent-agent-swarm/)]
- **Native Multimodality**: Pre-trained on 15 trillion text, image, and video tokens. Sub-agents don't just read text; they visually debug UI components, recreate full websites directly from video screencasts, and generate cross-modal charts. [[1](https://www.youtube.com/watch?v=FfCqINSD8Tc), [2](https://www.datacamp.com/tutorial/kimi-k2-agent-swarm-guide), [3](https://github.com/MoonshotAI/Kimi-K2.5), [4](https://www.kimi.com/blog/kimi-k2-5)]
