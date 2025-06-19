from lark import Lark, Transformer
import json

# Define the grammar again (same as in lexer.py)
aether_grammar = r"""
start: statement+

statement: agent_def

agent_def: "agent" CNAME "{" agent_body "}"

agent_body: memory_block? goal_block? event_block*

memory_block: "memory:" var_assign*

goal_block: "goal:" ESCAPED_STRING

event_block: "on" "event" ESCAPED_STRING "as" CNAME ":" "respond" "using" "GPT" ":" ESCAPED_STRING

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
        self.agent = {}

    def agent_def(self, items):
        name = items[0]
        self.agent["name"] = str(name)
        return self.agent
    def memory_block(self, items):
        self.agent["memory"] = dict(items)

    def var_assign(self, items):
        return (str(items[0]), items[1])

    def value(self, val):
        return val[0]

    def list(self, items):
        return list(items)

    def goal_block(self, items):
        self.agent["goal"] = str(items[0])[1:-1]

    def event_block(self, items):
        event_name = str(items[0])[1:-1]
        response = str(items[2])[1:-1]
        self.agent.setdefault("events", {})[event_name] = response

# Step 3: Simulate execution
def run_agent(agent):
    print(f"\n👾 Agent Name: {agent['name']}")
    print(f"🧠 Memory: {agent.get('memory', {})}")
    print(f"🎯 Goal: {agent.get('goal', '')}")

    while True:
        user_input = input("🗣️ Event: ")
        if user_input.lower() == "exit":
            print("👋 Exiting agent.")
            break

        event_key = "user_message"
        if event_key in agent.get("events", {}):
            template = agent["events"][event_key]
            response = template.replace("{message}", user_input)
            print(f"🤖 Response: {response}")
        else:
            print("🤖 No event handler for that input.")
# Step 4: Read and run
def main():
    with open("examples/hello.aether") as f:
        code = f.read()
    tree = parser.parse(code)
    transformer = AetherTransformer()
    transformer.transform(tree)
    agent = transformer.agent
    run_agent(agent)

if __name__ == "__main__":
    main()