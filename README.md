# AI Agents Workshop

A hands-on 3-day workshop on building AI agents with LangGraph. Each day
builds on the previous one — by the end you have a small multi-agent
system for reviewing pull requests.

## What we build

| Day | Focus |
|-----|-------|
| **Day 1** | A single coding agent that can read files, search code, and review git diffs. |
| **Day 2** | Extend the agent with a RAG knowledge base so it can review code against your team's standards. |
| **Day 3** | Wire everything into a multi-agent PR Review Team with a coordinator and parallel sub-agents. |

This repository contains the **Day 1** materials.

## Tech stack

- Python 3.11+
- LangGraph — agent orchestration
- LangChain — LLM interface and tools
- OpenAI GPT-4o-mini
- uv — Python package manager

## Quick start

```bash
# 1. Clone
git clone https://github.com/VikaDvornyk/AI_agents_workshops.git
cd AI_agents_workshops

# 2. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies
uv sync

# 4. Add your API key
cp .env.example .env
# then put your OPENAI_API_KEY into .env

# 5. Run Day 1
uv run python practice_day1/chat.py
```

See [practice_day1/README.md](practice_day1/README.md) for the step-by-step task breakdown.

## Windows users — one extra step

The scripts print Unicode characters (`→`, `↔`, em-dashes). On Windows the
default terminal codepage (cp1252 / cp866) can't encode them and you'll get
`UnicodeEncodeError`. Enable Python's UTF-8 mode **before** running anything:

```cmd
:: cmd.exe (current session)
set PYTHONUTF8=1

:: PowerShell (current session)
$env:PYTHONUTF8 = "1"

:: Persist for all future sessions
setx PYTHONUTF8 1
```

Also make sure `git` is installed and on `PATH` (Git for Windows does both).
`uv` install on Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`.
