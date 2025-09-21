from lark import Lark

aether_grammar = r"""
start: statement+

statement: agent_def | remember_block |forget_block

remember_block: "remember" ESCAPED_STRING "=" value

forget_block: "forget" ESCAPED_STRING

agent_def: "agent" CNAME "{" agent_body "}"

agent_body: memory_block? goal_block? think_block? reflect_block* event_block* schedule_block*

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

parser = Lark(aether_grammar, start="start")

def test_parser():
    with open("examples/hello.aether", "r") as f:
        code = f.read()
    tree = parser.parse(code)
    print(tree.pretty())

if __name__ == "__main__":
    test_parser()