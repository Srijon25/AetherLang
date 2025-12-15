# AetherLang

**An AI-native, agent-first DSL for GPT-powered agents with persistent memory and time-based scheduling.**

AetherLang is designed for a world where **agents**, **memory**, and **time** are first-class citizens.
It lets you write programs that can **think**, **reflect**, **respond**, and **remember across sessions**
using a natural, agent-oriented syntax and a small Python reference implementation.

---

## Features

- 🧠 **Agent-first model** — every program is an `agent` with memory + goal + behaviors.
- 💾 **Persistent memory** — stored as JSON in `memory/<agent>.json`, surviving across sessions.
- 🔄 **Reflection** — `reflect using gpt ...` queries the model without forcing a memory update.
- ⏳ **Scheduling** — `every Ns: recall "key"` for periodic recall/printing.
- 🖥️ **Dual interface** — CLI interpreter + PyQt5 GUI simulator.
- 🧩 **Minimal syntax** — designed to be readable and close to natural language.

---

## Quickstart (Run & Test)

### Step 0: Install Python & Clone Repository

Install Python 3.x (tested with modern versions) and ensure `python` is in your PATH.

Clone the repository:

```bash
git clone https://github.com/Srijon25/AetherLang.git
cd AetherLang
```

### Step 1: Create and Activate Virtual Environment

```bash
python -m venv venv
```

Linux / Mac:

```bash
source venv/bin/activate
```

Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

⚠️ Windows note: If you see “execution of scripts is disabled,” run PowerShell as Administrator:

```powershell
Set-ExecutionPolicy RemoteSigned
```
Type Y to confirm, then re-run activation.

### Step 2: Install Dependencies

Install the required Python packages:

# Required (CLI interpreter)
pip install lark-parser openai

# Optional (GUI support)
pip install PyQt5

# Optional (recommended if using .env files)
pip install python-dotenv

### Step 3: Set OpenAI API Key

**Recommended (secure):** set your API key via environment variables.

Linux / Mac:

```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

Windows (PowerShell):

```powershell
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

Windows (CMD):

```cmd
setx OPENAI_API_KEY "your_openai_api_key_here"
```

Create `aether/.env` file (for GUI/scripts):

```env
OPENAI_API_KEY=your_openai_api_key_here
```

⚠️ Security note: Do not share API keys.

### Step 4: Run CLI Interpreter

Run (default):

```bash
python aether/interpreter.py
```

By default, the reference implementation parses **`examples/hello.aether`** and then lists the agents found in that file. Select an agent number to enter the REPL.

Run a specific `.aether` file (optional):

```bash
python aether/interpreter.py examples/<file>.aether
```

Supported REPL Commands:

- `remember "key" = "value"` — adds or updates memory immediately  
- `forget "key"` — deletes a memory entry immediately  
- `reflect using gpt "..."` — produces GPT-powered reflection **without** updating memory (unless you manually remember something)  
- type an event name (e.g., `hello`) — triggers matching `on event "..."` handlers  
- `exit` — saves memory (if needed) and exits

### Step 5: Run GUI (optional)

```bash
python aether/gui.py
```

The GUI uses the same `memory/<agent>.json` persistence folder as the CLI.

```

✅ remember / forget and event-triggered runs persist (and create) memory/<agent>.json immediately. 
ℹ️ `reflect using gpt ...` does not force a memory update.

### 4) Run the GUI (optional)

```bash
python aether/gui.py
```

The GUI reads/writes the same `memory/<agent>.json` files as the CLI.

### 5) Parse-only mode (debugging the grammar)

```bash
python aether/lexer.py
```

---

## Writing agents

Agents live in `.aether` files (see `examples/hello.aether`). Minimal example:

```aether
agent MyAgent {
  memory:
    name = "Srijon"
  goal: "Learn faster"

  think using GPT: "Suggest 3 study plans for my goal."
  reflect using GPT: "Given my memory and goal, what's the next best action?"

  on event "hello" as handle_input:
    respond using GPT: "You said hello, {name}!"

  every 60s: recall "goal"
}
```

---

## How memory persistence works

- On startup, the interpreter loads `memory/<agent>.json` if it exists.
- If no file exists, it uses the initial `memory:` block from the `.aether` agent definition.
- Updates happen via:
  - `remember "k" = "v"` (immediate save),
  - `forget "k"` (immediate save),
  - event handling (optionally merges a JSON key/value update suggested by GPT).
- `exit` saves memory before quitting.

---

## Project structure

```text
AetherLang/
├── aether/
│   ├── lexer.py        # Grammar & parser (Lark)
│   ├── interpreter.py  # CLI interpreter + persistence + scheduler
│   ├── gui.py          # PyQt5 interactive GUI simulator
│   └── gpt_engine.py   # OpenAI API wrapper (edit/configure your key)
├── memory/             # JSON memory files created at runtime
├── examples/
│   └── hello.aether    # Example agents
├── docs/               # Screenshots / recordings
├── README.md
└── spec.md             # Language specification
```

---

## Documentation

- **Language specification:** `spec.md`
- **Example agents:** `examples/hello.aether`
- **Screenshots / demos:** `docs/`

---

## Demo recordings

Recordings are stored in `docs/recordings/`.

- **Create an agent (new `examples/*.aether` file) + run in CLI and GUI:**  
[AetherLang_create_agent_full_demo.mp4](docs/recordings/AetherLang_create_agent_full_demo.mp4)

(On GitHub, this will appear as a downloadable video file.)

---

## Known issues (current)

- Grammar is duplicated between `lexer.py` and `interpreter.py` (planned to unify).
- `reflect using gpt ...` does not automatically update memory JSON (by design).
- Input normalization (e.g., lowercasing events/keys consistently) is still evolving.
- More unit tests are needed for parser, persistence, and scheduling.

---

## Roadmap

- ✅ Week 1 — Setup & lexer
- ✅ Week 2 — Interpreter (parse + transform + run)
- ✅ Week 3 — GPT integration (respond / think / reflect)
- ✅ Week 4 — Scheduling (`every Ns: recall ...`)
- ✅ Week 5 — Persistent memory across sessions
- ✅ Week 6 — PyQt5 GUI simulator
- ✅ Week 7 — Specification + docs
- ✅ Week 8 — Release packaging + archival (e.g., Zenodo)

---

## Contributing

Contributions, bug reports, and feature requests are welcome.
If you open a PR, please describe the change clearly and include a small `.aether` example if relevant.

---

## License

MIT License © 2025 Srijon Kumar Shill

---

## Acknowledgments

Built to explore programming beyond code: agents that think, remember, and evolve.
