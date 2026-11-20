# F.R.I.D.A.Y. — AI Voice Assistant

> *"Fully Responsive Intelligent Digital Assistant for You"*

## Credits & Inspiration

This project is a **fork and extension** of the original [**friday-tony-stark-demo**](https://github.com/SAGAR-TAMANG/friday-tony-stark-demo) by [**Sagar Tamang**](https://github.com/SAGAR-TAMANG). Full credit to him for the original architecture, the MCP + LiveKit pipeline design, and the Tony Stark–inspired concept.

**Original demo by Sagar Tamang:**
- [Instagram Reel](https://www.instagram.com/p/DW2HjYtkwg_/)
- [YouTube Video Guide](https://www.youtube.com/watch?v=mMY9swqe3BI)

[![Original Demo Video](https://img.youtube.com/vi/mMY9swqe3BI/maxresdefault.jpg)](https://www.youtube.com/watch?v=mMY9swqe3BI)

---

## What We Changed & Added

We took Sagar's original project and customized it to run with **zero paid API costs** and work seamlessly on Windows. Here's everything we modified:

### 1. Free Edge TTS Adapter (`edge_tts_adapter.py`) — *New file*
The original required **OpenAI's paid TTS API** (`tts-1` / `nova` voice) which costs credits on every spoken response. We wrote a custom LiveKit-compatible TTS adapter from scratch that uses **Microsoft Edge's free Neural TTS** (`en-US-AriaNeural`). It decodes the MP3 stream into raw 24kHz PCM audio using PyAV so LiveKit can stream it — completely free, unlimited usage, no API key needed.

### 2. Groq / Llama 3.3 70B LLM Support (`agent_friday.py`) — *Modified*
Added a new LLM provider route for **Groq** running `llama-3.3-70b-versatile` via their blazing-fast inference API. The original only supported Gemini and OpenAI. We also added **Google Gemini TTS** as an additional voice option.

**Provider changes (original → ours):**
| Component | Original Default | Our Default |
|-----------|-----------------|-------------|
| LLM | Gemini 2.5 Flash | Groq (Llama 3.3 70B) |
| TTS | OpenAI TTS (paid) | Edge TTS (free) |
| TTS Voice | `nova` | `en-US-AriaNeural` |
| Sarvam Speaker | `rahul` | `meera` |

### 3. Local LiveKit Dev Tools — *New files*
- **`check_rooms.py`** — Utility to inspect active LiveKit rooms and participant counts.
- **`gen_token.py`** — JWT token generator for the local LiveKit dev server.

### 4. One-Click Windows Launcher (`start_friday.bat`) — *New file*
A batch script that launches both the MCP Server and Voice Agent into separate terminal windows with a single double-click, with step-by-step instructions printed in the console.

### 5. Personalized Persona
Customized FRIDAY's system prompt with a unique personality — calm, composed, occasionally dry humor. Wired trigger phrases like *"What did I miss?"* and *"Market news"* to automatically launch live visual dashboards.

---

## How It Works

```
Microphone ──► STT (Sarvam Saaras v3)
                    │
                    ▼
             LLM (Groq / Llama 3.3)  ◄──────► MCP Server (FastMCP / SSE)
                    │                              ├─ get_world_news
                    ▼                              ├─ open_world_monitor
             TTS (Edge Neural TTS)                 ├─ search_web
                    │                              ├─ get_world_finance_news
                    ▼                              └─ …more tools
             Speaker / LiveKit room
```

A Tony Stark–inspired AI assistant split into two cooperating pieces:

| Component | What it is |
|-----------|-----------|
| **MCP Server** (`uv run friday`) | A [FastMCP](https://github.com/jlowin/fastmcp) server that exposes tools (news, web search, finance, system info, …) over SSE. |
| **Voice Agent** (`uv run friday_voice`) | A [LiveKit Agents](https://github.com/livekit/agents) voice pipeline that listens to your microphone, reasons with an LLM, and speaks back — all while pulling tools from the MCP server in real time. |

The voice agent connects to the MCP server via SSE at `http://127.0.0.1:8000/sse`.

---

## Project Structure

```
friday-ai-voice-assistant/
├── server.py              # uv run friday  → starts the MCP server (SSE on :8000)
├── agent_friday.py        # uv run friday_voice → starts the LiveKit voice agent
├── edge_tts_adapter.py    # ★ Custom free Edge TTS adapter for LiveKit
├── start_friday.bat       # ★ One-click Windows launcher
├── check_rooms.py         # ★ LiveKit room inspector
├── gen_token.py           # ★ JWT token generator for local dev
├── pyproject.toml
├── .env.example           # copy → .env and fill in your keys
│
└── friday/                # MCP server package
    ├── config.py          # env-var loading & app-wide settings
    ├── tools/             # MCP tools (callable by the LLM)
    │   ├── web.py         # search_web, fetch_url, get_world_news, open_world_monitor
    │   ├── system.py      # get_current_time, get_system_info
    │   └── utils.py       # format_json, word_count
    ├── prompts/           # MCP prompt templates (summarize, explain_code, …)
    └── resources/         # MCP resources exposed to clients (friday://info)
```

> Files marked with ★ are our custom additions.

---

## Quick Start

### 1. Prerequisites

- Python ≥ 3.11
- [`uv`](https://github.com/astral-sh/uv) — `pip install uv` or `curl -Lsf https://astral.sh/uv/install.sh | sh`
- A [LiveKit Cloud](https://cloud.livekit.io) project (free tier works)

### 2. Clone & install

```bash
git clone https://github.com/Luvkumar9306/friday-ai-voice-assistant.git
cd friday-ai-voice-assistant
uv sync          # creates .venv and installs all dependencies
```

### 3. Set up environment

```bash
cp .env.example .env
# Open .env and fill in your API keys (see the section below)
```

### 4. Run

**Option A — One-click (Windows)**

Double-click `start_friday.bat` — it launches both servers automatically.

**Option B — Two terminals (any OS)**

**Terminal 1 — MCP server** (must start first)

```bash
uv run friday
```

**Terminal 2 — Voice agent**

```bash
uv run friday_voice
```

Open the [LiveKit Agents Playground](https://agents-playground.livekit.io) and connect to your room to talk to FRIDAY.

---

## `uv run friday` vs `uv run friday_voice`

| Command | Entry point | What it does |
|---------|------------|--------------|
| `uv run friday` | `server.py → main()` | Launches the **FastMCP server** over SSE transport on port 8000. This is the "brain backend" — it registers all tools, prompts, and resources that the LLM can call. |
| `uv run friday_voice` | `agent_friday.py → dev()` | Launches the **LiveKit voice agent**. It builds the STT / LLM / TTS pipeline, connects to your LiveKit room, and wires up the MCP server as a tool source. |

> Both processes must run **simultaneously**. The voice agent calls the MCP server in real time whenever it needs a tool.

---

## Environment Variables

Copy `.env.example` → `.env` and fill in the values below.

| Variable | Required | Where to get it |
|----------|----------|----------------|
| `LIVEKIT_URL` | ✅ | [LiveKit Cloud dashboard](https://cloud.livekit.io) → your project URL |
| `LIVEKIT_API_KEY` | ✅ | LiveKit Cloud → API Keys |
| `LIVEKIT_API_SECRET` | ✅ | LiveKit Cloud → API Keys |
| `GROQ_API_KEY` | ✅ (default LLM) | [console.groq.com](https://console.groq.com) |
| `SARVAM_API_KEY` | ✅ (default STT) | [dashboard.sarvam.ai](https://dashboard.sarvam.ai) |
| `OPENAI_API_KEY` | optional | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) — only if using OpenAI TTS |
| `GOOGLE_API_KEY` | optional | [aistudio.google.com](https://aistudio.google.com/projects) — only if using Gemini LLM/TTS |
| `DEEPGRAM_API_KEY` | optional | [console.deepgram.com](https://console.deepgram.com) |

---

## Switching Providers

Open `agent_friday.py` and change the provider constants at the top:

```python
STT_PROVIDER = "sarvam"   # "sarvam" | "whisper"
LLM_PROVIDER = "groq"     # "groq" | "gemini" | "openai"
TTS_PROVIDER = "edge"     # "edge" | "openai" | "sarvam" | "google"
```

---

## Adding a New Tool

1. Create or open a file in `friday/tools/`
2. Define a `register(mcp)` function and decorate tools with `@mcp.tool()`
3. Import and call `register(mcp)` inside `friday/tools/__init__.py`

The MCP server will pick it up on next start.

---

## Tech Stack

- **[FastMCP](https://github.com/jlowin/fastmcp)** — MCP server framework
- **[LiveKit Agents](https://github.com/livekit/agents)** — real-time voice pipeline
- **Sarvam Saaras v3** — STT (Indian-English optimised)
- **[Groq](https://groq.com)** — ultra-fast LLM inference (Llama 3.3 70B)
- **Microsoft Edge TTS** — free neural text-to-speech
- **[uv](https://github.com/astral-sh/uv)** — fast Python package manager

---

## License

MIT

---

## Acknowledgements

Built on top of the excellent [friday-tony-stark-demo](https://github.com/SAGAR-TAMANG/friday-tony-stark-demo) by [Sagar Tamang](https://github.com/SAGAR-TAMANG). Thank you for open-sourcing the original project and inspiring this fork.
