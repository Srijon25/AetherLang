# AetherLang

AetherLang is a time-native, AI-native programming language for intelligent systems and simulations.

## 🌟 Key Features

- Agent-based programming with memory and goals  
- Native GPT integration  
- Natural syntax for intelligent behavior  
- Designed for research, simulation, and creative AI  

## 💡 Example AetherLang Code

agent bot { memory: mood = "curious" history = []

goal:
    understand "quantum computing"

on event "question" as q:
    think using GPT:
        respond(q)
    history += q

}

## 📁 Project Structure

AetherLang/ ├── README.md ├── aether/ │   └── lexer.py └── examples/ └── hello.aether

## 🔧 Getting Started

Run the parser on example code:

```bash
python aether/lexer.py

Expected output: A parse tree of the AetherLang source file.