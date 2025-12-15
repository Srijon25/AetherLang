# aether/gui.py
import sys
import json
import os
import threading
import time
from pathlib import Path


from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QTextEdit, QLabel, QLineEdit, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject

# try to import your project's GPT engine and memory utils
try:
    from aether.gpt_engine import call_gpt
except Exception:
    
  from openai import OpenAI

  client = OpenAI()  # make sure your API key is set in aether/.env: OPENAI_API_KEY="..."
  

  def call_gpt(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",   # or "gpt-4o"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR calling GPT] {e}"

MEMORY_DIR = "memory"  # folder where agent JSON files are saved
EXAMPLES_FILE = "examples/hello.aether"  # optional parsed source for agent list
EXAMPLES_DIR = Path("examples")          # scan all .aether files here

# Utility: load all agent memory files in memory/
def available_agents():
    os.makedirs(MEMORY_DIR, exist_ok=True)
    agents = []
    for fname in os.listdir(MEMORY_DIR):
        if fname.endswith(".json"):
            agents.append(fname[:-5])
    return agents

def load_agent_memory(agent_name):
    path = os.path.join(MEMORY_DIR, f"{agent_name}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_agent_memory(agent_name, mem):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    path = os.path.join(MEMORY_DIR, f"{agent_name}.json")
    with open(path, "w") as f:
        json.dump(mem, f, indent=2)

# Simple logic that builds prompt for GPT using memory & goal (adapt to your interpreter)
def build_prompt(agent_name, agent_memory, agent_goal, user_input, template=None):
    memory_str = json.dumps(agent_memory, indent=2)
    if template:
        # replace {message} and {memory} placeholders if present
        prompt_style = template.replace("{message}", user_input).replace("{memory}", memory_str)
    else:
        prompt_style = f'User input: "{user_input}"\n\nMemory:\n{memory_str}\n\nGoal:\n{agent_goal}'
    return prompt_style

def load_agent_def_from_examples(agent_name: str):
    """
    Find the first agent definition with this name by parsing examples/*.aether.
    Returns the parsed agent dict (may include goal/events/schedule), or None.
    """
    # robust import (works when running `python aether/gui.py` from repo root)
    try:
        from aether.interpreter import parser, AetherTransformer
    except Exception:
        from interpreter import parser, AetherTransformer  # fallback if you run from inside aether/

    if not EXAMPLES_DIR.exists():
        return None

    for path in sorted(EXAMPLES_DIR.glob("*.aether")):
        try:
            code = path.read_text(encoding="utf-8")
            tree = parser.parse(code)
            transformer = AetherTransformer()
            agents = transformer.transform(tree)
            for ag in agents:
                if ag.get("name") == agent_name:
                    return ag
        except Exception as e:
            print(f"⚠️ Could not parse {path}: {e}")

    return None

# Signals object to communicate between thread and UI
class Signals(QObject):
    append_history = pyqtSignal(str)
    update_memory = pyqtSignal(dict)
    update_response = pyqtSignal(str)


signals = Signals()

class AetherGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AetherLang — Agent Simulator")
        self.resize(900, 600)

        self.agent_memory = {}
        self.agent_name = None

        layout = QHBoxLayout()
        left = QVBoxLayout()
        right = QVBoxLayout()

        # Agent selector and reload
        top_row = QHBoxLayout()
        self.agent_select = QComboBox()
        self.reload_agents()
        top_row.addWidget(QLabel("Agent:"))
        top_row.addWidget(self.agent_select)
        self.reload_btn = QPushButton("Reload Agents")
        self.reload_btn.clicked.connect(self.reload_agents)
        top_row.addWidget(self.reload_btn)
        left.addLayout(top_row)

        # Memory view
        left.addWidget(QLabel("Memory"))
        self.memory_view = QTextEdit()
        self.memory_view.setReadOnly(True)
        left.addWidget(self.memory_view)

        # Goal
        left.addWidget(QLabel("Goal"))
        self.goal_view = QLabel("<no goal>")
        left.addWidget(self.goal_view)

        # Buttons to remember/forget quickly
        mem_buttons = QHBoxLayout()
        self.remember_key = QLineEdit()
        self.remember_key.setPlaceholderText("key")
        self.remember_val = QLineEdit()
        self.remember_val.setPlaceholderText("value")
        mem_buttons.addWidget(self.remember_key)
        mem_buttons.addWidget(self.remember_val)
        self.remember_btn = QPushButton("Remember")
        self.remember_btn.clicked.connect(self.remember_now)
        mem_buttons.addWidget(self.remember_btn)
        self.forget_btn = QPushButton("Forget Key")
        self.forget_btn.clicked.connect(self.forget_now)
        mem_buttons.addWidget(self.forget_btn)
        left.addLayout(mem_buttons)

        # Extra agent actions
        actions_row = QHBoxLayout()
        self.reflect_btn = QPushButton("Reflect")
        self.reflect_btn.clicked.connect(self.reflect_now)
        actions_row.addWidget(self.reflect_btn)

        self.think_btn = QPushButton("Think")
        self.think_btn.clicked.connect(self.think_now)
        actions_row.addWidget(self.think_btn)

        left.addLayout(actions_row)

        # Decision history
        right.addWidget(QLabel("Decision History"))
        self.history = QListWidget()
        right.addWidget(self.history)

        # Input and send
        input_row = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type event (e.g., 'hello') or message")
        input_row.addWidget(self.input_line)
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_input)
        input_row.addWidget(self.send_btn)
        right.addLayout(input_row)

        # Response display
        right.addWidget(QLabel("Last Response"))
        self.response_view = QTextEdit()
        self.response_view.setReadOnly(True)
        right.addWidget(self.response_view)

        layout.addLayout(left, 2)
        layout.addLayout(right, 3)
        self.setLayout(layout)

        # connect signals
        signals.append_history.connect(self.append_history)
        signals.update_memory.connect(self.show_memory)
        signals.update_response.connect(self.show_response)

        # start recall scheduler
        threading.Thread(target=self.recall_scheduler, daemon=True).start()

        # load initial agent
        self.load_selected_agent()

        # when agent selection changes
        self.agent_select.currentIndexChanged.connect(self.load_selected_agent)

    def reload_agents(self):
        self.agent_select.clear()
        agents = available_agents()
        if not agents:
            # if no agents exist, create a sample memory file from examples
            sample = "MyAgent"
            os.makedirs(MEMORY_DIR, exist_ok=True)
            save_agent_memory(sample, {"name": sample, "goal": "Win MIT Scholarship"})
            agents = available_agents()
        self.agent_select.addItems(agents)

    def load_selected_agent(self):
        name = self.agent_select.currentText()
        if not name:
          return
        self.agent_name = name
        self.agent_memory = load_agent_memory(name)

        # ⬇️ Load schedule/goal/events from ANY examples/*.aether file (not only hello.aether)
        ag = load_agent_def_from_examples(self.agent_name)
        if ag:
            if "schedule" in ag:
                self.agent_memory["schedule"] = ag["schedule"]

            # if schedule recalls "goal", GUI needs goal too
            if "goal" in ag and "goal" not in self.agent_memory:
                self.agent_memory["goal"] = ag["goal"]

            # optional but helpful: enable event templates in GUI
            if "events" in ag and "events" not in self.agent_memory:
                self.agent_memory["events"] = ag["events"]
        else:
            print("⚠️ No agent definition found in examples/*.aether for:", self.agent_name)

        # show memory and goal
        self.show_memory(self.agent_memory)
        self.goal_view.setText(self.agent_memory.get("goal", "<no goal>"))
        self.history.clear()

    def show_memory(self, mem):
        pretty = json.dumps(mem, indent=2)
        self.memory_view.setPlainText(pretty)

    def append_history(self, text):
        self.history.addItem(text)
        self.history.scrollToBottom()

    def remember_now(self):
        k = self.remember_key.text().strip()
        v = self.remember_val.text().strip()
        if not k:
            QMessageBox.warning(self, "Remember", "Please enter a key.")
            return
        self.agent_memory[k] = v
        save_agent_memory(self.agent_name, self.agent_memory)
        signals.update_memory.emit(self.agent_memory)
        signals.append_history.emit(f"🧠 Remembered: {k} = {v}")
        self.remember_key.clear()
        self.remember_val.clear()

    def forget_now(self):
        k = self.remember_key.text().strip()
        if not k:
            QMessageBox.warning(self, "Forget", "Please enter a key to forget.")
            return
        popped = self.agent_memory.pop(k, None)
        save_agent_memory(self.agent_name, self.agent_memory)
        signals.update_memory.emit(self.agent_memory)
        signals.append_history.emit(f"🗑️ Forgot: {k} (was: {popped})")
        self.remember_key.clear()
        self.remember_val.clear()

    def reflect_now(self):
        """Ask GPT to reflect on agent memory & goal"""
        threading.Thread(target=self._reflect_bg, daemon=True).start()

    def _reflect_bg(self):
        goal = self.agent_memory.get("goal", "")
        mem_str = json.dumps(self.agent_memory, indent=2)
        prompt = f"Reflect on this agent's state.\nGoal: {goal}\nMemory:\n{mem_str}"
        try:
          resp = call_gpt(prompt)
        except Exception as e:
          resp = f"[ERROR in reflection] {e}"
        signals.append_history.emit(f"🪞 Reflection: {resp}")
        signals.update_response.emit(resp)

    def think_now(self):
       """Ask GPT to generate a free-form thought"""
       threading.Thread(target=self._think_bg, daemon=True).start()

    def _think_bg(self):
       goal = self.agent_memory.get("goal", "")
       prompt = f"Think step-by-step about how to achieve the goal: {goal}"
       try:
        resp = call_gpt(prompt)
       except Exception as e:
        resp = f"[ERROR in thinking] {e}"
       signals.append_history.emit(f"💭 Thought: {resp}")
       signals.update_response.emit(resp)   

    def send_input(self):
        user_text = self.input_line.text().strip()
        if not user_text:
            return
        # run the agent handling in a background thread to avoid blocking UI
        threading.Thread(target=self.handle_input_bg, args=(user_text,), daemon=True).start()
        self.input_line.clear()

    def handle_input_bg(self, user_text):
       goal = self.agent_memory.get("goal", "")
       template = None
       events = self.agent_memory.get("events", {}) if isinstance(self.agent_memory.get("events", {}), dict) else {}
       if user_text.lower() in events:
          template = events[user_text.lower()]

       prompt = build_prompt(self.agent_name, self.agent_memory, goal, user_text, template)
       signals.append_history.emit(f"🗣️ You: {user_text}")

       # Call GPT
       try:
          resp = call_gpt(prompt)
       except Exception as e:
          resp = f"[ERROR calling GPT] {e}"

       # Show GPT response
       signals.append_history.emit(f"🤖 Agent: {resp}")
       signals.update_response.emit(resp)

       # 🔄 Try to parse JSON memory update from GPT response
       try:
          parsed = json.loads(resp)
          if isinstance(parsed, dict):
            self.agent_memory.update(parsed)
            save_agent_memory(self.agent_name, self.agent_memory)
            signals.update_memory.emit(self.agent_memory)
            signals.append_history.emit("📥 Memory auto-updated from GPT response")
       except Exception:
         # if resp is not valid JSON, just ignore
         pass

       # refresh memory view
       signals.update_memory.emit(self.agent_memory)

    def recall_scheduler(self):
      """Background loop to check for scheduled recalls in memory"""
      while True:
        schedules = self.agent_memory.get("schedule", [])
        now = int(time.time())
        for interval, key in schedules:
            # Use a unique key to track last trigger time
            last_key = f"last_{key}_{interval}"
            last = self.agent_memory.get(last_key, 0)
            if now - last >= interval:
                # Get value from memory or goal
                value = self.agent_memory.get(key, None)
                if value is None and key == "goal":
                    value = self.agent_memory.get("goal", "[Unknown]")
                elif value is None:
                    value = "[Unknown]"

                # Emit to history
                signals.append_history.emit(f"⏰ Recall: {key} ➜ {value}")

                # Update last trigger time
                self.agent_memory[last_key] = now
                save_agent_memory(self.agent_name, self.agent_memory)
                signals.update_memory.emit(self.agent_memory)

        time.sleep(2)    
    
    def show_response(self, text):
        self.response_view.setPlainText(text)

def main():
    app = QApplication(sys.argv)
    gui = AetherGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
