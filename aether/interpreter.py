from gpt_engine import call_gpt
from lark import Lark, Transformer
import threading
import time
import json
import os

def load_memory(agent_name):
    path = f"memory/{agent_name}.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def save_memory(agent_name, memory):
    os.makedirs("memory", exist_ok=True)
    with open(f"memory/{agent_name}.json", "w") as f:
     json.dump(memory, f, indent=2)
      
# Define the grammar again (same as in lexer.py)
aether_grammar = r"""
start: statement+

statement: agent_def | remember_block

remember_block: "remember" ESCAPED_STRING "=" value

agent_def: "agent" CNAME "{" agent_body "}"

agent_body: memory_block? goal_block? think_block? reflect_block? event_block* schedule_block*

memory_block: "memory:" var_assign*

goal_block: "goal:" ESCAPED_STRING

think_block: "think" "using" "GPT" ":" ESCAPED_STRING

reflect_block: "reflect" "using" "GPT" ":" ESCAPED_STRING

event_block: "on" "event" ESCAPED_STRING "as" CNAME ":" "respond" "using" "GPT" ":" ESCAPED_STRING

schedule_block: "every" SIGNED_NUMBER "s:" "recall" ESCAPED_STRING

var_assign: CNAME "=" value

value: ESCAPED_STRING | SIGNED_NUMBER | list

list: "[" [value ("," value)*] "]"

%import common.CNAME
%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING
%import common.WS
%ignore WS
"""

# Step 1: Parse the code
parser = Lark(aether_grammar, start="start")

# Step 2: Transform tree into Python objects
class AetherTransformer(Transformer):
    def __init__(self):
        self.agents = []
        self.current_agent = {}

    def agent_def(self, items):
        name = items[0]
        self.current_agent["name"] = str(name)
        self.agents.append(self.current_agent)
        self.current_agent = {}  # Reset for next agent

    def memory_block(self, items):
        self.current_agent["memory"] = dict(items)

    def var_assign(self, items):
        return (str(items[0]), items[1])

    def value(self, val):
        v = val[0]
        if v.type == 'ESCAPED_STRING':
         return v[1:-1]  # strip surrounding quotes
        return float(v) if v.type == 'SIGNED_NUMBER' else str(v)

    def list(self, items):
        return list(items)

    def goal_block(self, items):
        self.current_agent["goal"] = str(items[0])[1:-1]

    def event_block(self, items):
        event_name = str(items[0])[1:-1]
        response = str(items[2])[1:-1]
        self.current_agent.setdefault("events", {})[event_name] = response

    def start(self, items):
        return self.agents  # Return all agents
    
    def think_block(self, items):
        self.current_agent["thought"] = str(items[0])[1:-1]

    def reflect_block(self, items):
        self.current_agent["reflect"] = str(items[0])[1:-1]    

    def schedule_block(self, items):
        interval = int(items[0])
        key = str(items[1])[1:-1]  # remove quotes from key
        self.current_agent.setdefault("schedule", []).append((interval, key))    

# Step 3: Simulate execution
def run_agent(agent):

    agent["memory"] = load_memory(agent["name"]) or agent.get("memory", {})
    
    print(f"\n👾 Agent Name: {agent['name']}")
    print(f"🧠 Memory loaded: {agent['memory']}")
    print(f"🎯 Goal: {agent.get('goal', '')}")

    # ⏰ Background scheduler for time-based recalls
    def run_schedule(agent):
        for interval, key in agent.get("schedule", []):
            print(f"👀 Starting scheduled recall every {interval}s for key '{key}'")

            def task(interval=interval, key=key):
                while True:
                    time.sleep(interval)
                    if key in agent.get("memory", {}):
                     value = agent["memory"][key]
                    elif key == "goal":
                     value = agent.get("goal")
                    else:
                     value = "[Unknown]"

                    print(f"\n⏰ Scheduled recall [{interval}s]: {key} ➜ {value}")
            threading.Thread(target=task, daemon=True).start()

    # ✅ Start the schedule thread
    run_schedule(agent)

    # 🧠 Start the interaction loop
    while True:
        user_input = input("🗣️ Event: ").strip().lower()
        if user_input == "exit":
            print("👋 Exiting agent.")

            save_memory(agent["name"], agent.get("memory", {}))
    

            break
        # 🧠 Handle dynamic memory: remember "key" = "value"
        if user_input.startswith("remember "):
         try:
             _, rest = user_input.split("remember ", 1)
             key, value = rest.split("=", 1)
             key = key.strip().strip('"')
             value = value.strip().strip('"')
             agent.setdefault("memory", {})[key] = value
             save_memory(agent["name"], agent["memory"])
             print(f"🧠 Remembered: {key} = {value}")
         except Exception as e:
                print("⚠️ Invalid remember syntax. Use: remember \"key\" = \"value\"")
            
                continue
        if user_input in agent.get("events", {}): 
            # 🧠 GPT thinking
            if "thought" in agent:
                print("🧠 Agent is thinking...")
                memory_snapshot = ", ".join(f"{k}: {v}" for k, v in agent.get("memory", {}).items())
                thinking_prompt = f"""
Agent memory: {memory_snapshot}
User said: "{user_input}"
Think: {agent['thought']}
"""
                thought = call_gpt(thinking_prompt)
                print(f"🧠 Thought: {thought}")

            # 🧩 Process template
            template = agent["events"][user_input]
            memory = agent.get("memory", {})
            goal = agent.get("goal", "None")

            for k, v in memory.items():
                template = template.replace(f"{{{k}}}", str(v))

            memory_str = ", ".join(f"{k}: {v}" for k, v in memory.items())

            prompt = f"""
You are an AI agent with the goal: "{goal}"
Your memory: {memory_str}
The user said: "{user_input}"
Respond using this template: "{template}"
"""
            response = call_gpt(prompt)
            print(f"🤖 Response: {response}")

            # 🧠 Memory update
            update_prompt = f"""
Here is the current memory: {memory_str}
User said: "{user_input}"
Agent responded: "{response}"
Suggest ONE key-value update to the memory. Format as JSON: {{"key": "value"}}
If no update, return {{}}
"""
            mem_update = call_gpt(update_prompt)
            try:
                update = json.loads(mem_update)
                agent["memory"].update(update)
                
                if update:
                    print(f"🧠 Memory updated: {update}")
            except:
                print("⚠️ Could not update memory.")

            # 🪞 Reflection
            if "reflect" in agent:
                reflect_prompt = f"""
Agent memory:
{json.dumps(agent.get('memory', {}), indent=2)}

Goal: {agent.get('goal', '')}

Now: {agent['reflect']}
"""
                reflection = call_gpt(reflect_prompt)
                print(f"🪞 Reflection: {reflection}")
        else:
            print("🤖 No event handler for that input.")

        
# Step 4: Read and run
def main():
    with open("examples/hello.aether") as f:
        code = f.read()
    
    tree = parser.parse(code)
    transformer = AetherTransformer()           # ✅ 1. Create transformer
    agents = transformer.transform(tree)        # ✅ 2. Parse agents
    
    print("🤖 Available Agents:")
    for i, ag in enumerate(agents):             # ✅ 3. Show agent list
        print(f"  {i+1}. {ag['name']}")

    selected = int(input("Select agent number: ")) -1
    run_agent(agents[selected])                 # ✅ 4. Run selected agent



if __name__ == "__main__":
    main()