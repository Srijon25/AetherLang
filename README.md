📘 AetherLang

AI-Native, Time-Native, Agent-First, Memory-Persistent Programming Language

AetherLang is not just another programming language — it’s designed for a world where agents, memory, and 
time are first-class citizens. Unlike Python, Java, or C++, AetherLang lets you write programs that 
think, remember, and evolve over time. With built-in GPT reasoning, persistent memory across sessions, 
and natural-language-friendly syntax, it enables developers to create autonomous systems, simulations, 
and adaptive AI agents in a way that traditional languages simply can’t.




✨ Features

🧠 Agent-First Model – every program is an agent with memory.

💾 Persistent Memory – stored in memory/agent.json, surviving across sessions.

🔄 Reflection – reflect commands query GPT, but do not persist to JSON.

⏳ Time & Scheduling – every 5 seconds do ... or on exit say ....

🖥️ Dual Interface – run via CLI or interactive PyQt5 GUI.

📝 Minimal Syntax – one statement per line, bridging natural language and code.




🔧 Getting Started

1.Clone & Install

git clone https://github.com/Srijon25/AetherLang.git
cd AetherLang

# create virtual environment
python -m venv venv
source venv/bin/activate       # Windows: .\venv\Scripts\Activate.ps1

# Install dependencies
pip install lark-parser PyQt5 openai python-dotenv


2.Set OpenAI API Key

Create a .env file:

OPENAI_API_KEY=your_openai_api_key_here


Or set it in terminal:

# Linux / Mac
export OPENAI_API_KEY=your_openai_api_key_here  

# Windows
setx OPENAI_API_KEY "your_openai_api_key_here"


⚠️ Both .env and terminal methods should use the same key to ensure CLI + GUI share memory.

3.Run Interpreter (CLI)

python aether/interpreter.py


Example REPL commands:

remember "goal" = "Win MIT Scholarship"
reflect using gpt "What’s my next best step?"
forget "goal"
exit


💾 All changes persist automatically and create memory/<agent>.json (except reflect using gpt"...").

4.Run GUI (optional)

python aether/gui.py


Same memory persistence as CLI — closing the window saves state.

5.Run Parser Only

python aether/lexer.py


Outputs a parse tree for .aether source files.

📖 For a step-by-step Quickstart (with venv setup, prerequisites, and persistence notes), see spec.md




📂 Project Structure
AetherLang/
├── aether/
│   ├── lexer.py        # Grammar & parser (Lark)
│   ├── interpreter.py  # Executes AetherLang programs
│   ├── gui.py          # PyQt5 interactive GUI
│   ├── gpt_engine.py   # GPT integration
│   └── .env 
├── memory/
│   └── agent.json      # Persistent agent memory
├── examples/
│   ├── hello.aether    # example agents
│
├── docs/               # screenshots
├── README.md
└── spec.md             # Language specification




📖 Documentation

Full language specification: spec.md

Screenshots & demos: docs/

Example programs: examples/




🧪 Examples

Run included agents from examples/hello.aether:

MyAgent — scholarship-focused self-reflective agent

TutorBot — adaptive subject tutor

HealthHelper — mental health support agent



👉 To create your own agents, see 4.1 Authoring New Agents in the full specification (spec.md)





⚠️ Known Issues

Grammar duplicated between lexer.py and interpreter.py

reflect using gpt does not update memory JSON

Input normalization (e.g., lowercase keys) is pending

More unit tests needed




🗺️ Roadmap — 8-Week MIT Scholarship Plan

Project Goal: Build the world’s first AI-native, time-native programming language, capable of defining 
memory, goals, and dynamic GPT reasoning — usable for agents, simulations, and autonomous systems.

✅ Week 1 — Setup & Lexer

🚀 Week 2 — Interpreter (AST traversal, agent simulation)

🧠 Week 3 — GPT integration (respond, think, reflect)

⏳ Week 4 — Time-native features (scheduled events)

🧬 Week 5 — Persistent memory, knowledge & reflection

🤖 Week 6 — PyQt5 visual agent simulator (GUI)

📚 Week 7 — Write official specification + docs

🔬 Week 8 — Publish academic paper & project repository (both with Zenodo DOI)




🤝 Contributing

Contributions, bug reports, and feature requests are welcome.
Please check the roadmap before submitting a PR.




📜 License

MIT License © 2025 Srijon Kumar Shill




🌟 Acknowledgments

Inspired by conversations with AI agents.

Built to explore programming beyond code: agents that think, remember, and evolve.