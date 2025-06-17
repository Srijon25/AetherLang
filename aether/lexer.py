from lark import Lark

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

parser = Lark(aether_grammar, start="start")

def test_parser():
    with open("examples/hello.aether", "r") as f:
        code = f.read()
    tree = parser.parse(code)
    print(tree.pretty())

if __name__ == "__main__":
    test_parser()