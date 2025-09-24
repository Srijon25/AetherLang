AetherLang — Official Language Specification 

Table of contents

1. Introduction & motivation


2. Quickstart (run & test)


3. Language overview (core concepts)


4. Concrete syntax (examples from hello.aether)


5. Formal grammar (EBNF & Lark)


6. Execution model & semantics


7. GPT prompt conventions


8. Memory, persistence & scheduling semantics


9. Error messages & debugging tips


10. Interactive examples


11. Known issues & recommended fixes





1. Introduction & Motivation

AetherLang is an AI-native, agent-first programming language designed around persistent memory, declarative goals, and seamless integration with large language models (GPT). Unlike traditional languages that treat GPT as an external service, AetherLang elevates it to a first-class primitive, enabling agents that can think, reflect, and respond while preserving continuity across sessions.

Key points:

First-class agent abstraction with persistent memory.

Built-in GPT primitives: remember, forget, reflect, respond, think.

Time-native constructs (every <N>s: recall <key>) for recurring behaviors.





2. Quickstart (Run & Test)

Prerequisites

Python 3.13+

Recommended: create a virtual environment

pip install lark-parser PyQt5 openai python-dotenv

Step 0: Set OpenAI API Key

In .env file (for GUI or scripts):

OPENAI_API_KEY=your_openai_api_key_here


In terminal environment (for CLI interpreter):

Linux / Mac:

export OPENAI_API_KEY=your_openai_api_key_here


Windows (PowerShell):

$env:OPENAI_API_KEY="your_openai_api_key_here"


Windows (CMD):

setx OPENAI_API_KEY "your_openai_api_key_here"


⚠️ Both .env and terminal environment should use the same API key to ensure CLI and GUI access the same GPT account and memory functions correctly.

Step 1: Create and Activate Virtual Environment
# Create venv
python -m venv venv

# On Linux / Mac
source venv/bin/activate

# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1


⚠️ Windows note: If you see “execution of scripts is disabled,” open PowerShell as Administrator and run:

Set-ExecutionPolicy RemoteSigned


Type Y to confirm, then re-run activation.

Step 2: Run CLI Interpreter
python aether/interpreter.py


Select an agent from examples/hello.aether.

Supported REPL Commands:

remember "key" = "value"       — adds or updates memory immediately
forget "key"                    — deletes memory entry immediately
reflect using gpt "..."          — Produces GPT-powered reflection without updating memory.
on event "..."                   — triggers event-based response
exit                             — saves current memory to memory/<agent>.json and exits


Memory Persistence Notes:

Any command that modifies memory (remember, forget, or event responses) automatically creates or updates memory/<agent>.json.

If no memory-modifying commands are typed, using exit will still create the memory file with the agent’s current state.

GUI interactions also update memory/<agent>.json automatically; closing the window saves memory if not already updated.


Step 3: Run GUI (optional)

python aether/gui.py

All interactions in the GUI update the same memory file as the CLI (memory/<agent>.json).

Closing the GUI automatically persists memory.





3. Language Overview (Core Concepts)

AetherLang is an AI-native, time-native agent language. Its building blocks are:

agent — execution unit with name, memory, optional goal, and behaviors. Persisted to memory/<agent>.json.

memory — key-value store that survives across sessions.

goal — high-level string objective guiding the agent.

remember "key" = "value" — add/update memory (REPL command).

forget "key" — delete memory entry (REPL command).

think using GPT — generate new ideas via GPT.

reflect using GPT — structured reflection on memory + goal.

In .aether files: predefined self-reflection.

In REPL: ad-hoc queries like reflect using gpt "What is my current goal?".


on event "..." — event handler mapping input to responses.

respond using GPT — generate GPT-based replies for events.

every N s: recall "key" — time-native scheduling for periodic memory recall.

exit — saves the agent’s memory to JSON and closes session.





4. Concrete Syntax (from hello.aether)

agent MyAgent {
  memory:
    name = "Srijon Kumar Shill"
    age = 17
  goal: "Win MIT Scholarship"
  think using GPT: "Think of 3 creative strategies a 17-year-old can use to get a full MIT scholarship."
  reflect using GPT: "Given my memory and goal, what's the smartest next action I should take?"
  on event "hello" as handle_input:
    respond using GPT: "You said hello, {name}!"
  every 60s: recall "goal"
}

agent TutorBot {
  memory:
    subject = "Math"
    level = "High School"
  goal: "Help students learn effectively"
  think using GPT: "Think of 3 methods to make {subject} more engaging for {level} students."
  reflect using GPT: "How can I evolve to become a more helpful {subject} tutor for {level} students?"
  on event "ask" as handle_input:
    respond using GPT: "I'm your {subject} tutor. You asked a question."
  every 70s: recall "subject"
}

agent HealthHelper {
  memory:
    name = "FitAI"
    focus = "mental health"
  goal: "Improve user well-being"
  think using GPT: "Come up with a daily check-in strategy to improve user {focus}."
  reflect using GPT: "How can I better understand and support the user's {focus}?"
  on event "status" as handle_input:
    respond using GPT: "Hi, I'm {name}, your assistant for {focus}. How are you feeling?"
  every 75s: recall "focus"
}





5. Formal grammar (EBNF & Lark)

EBNF:

<program>         ::= <statement>+
<statement>       ::= <agent> | <remember> | <forget>

<remember>        ::= "remember" STRING "=" <value>
<forget>          ::= "forget" STRING

<agent>           ::= "agent" IDENT "{" <agent-body> "}"
<agent-body>      ::= <memory-block>? <goal-block>? <think-block>? <reflect-block>* <event-block>* <schedule-block>*

<memory-block>    ::= "memory:" <var-assign>*
<goal-block>      ::= "goal:" STRING
<think-block>     ::= "think using GPT:" STRING
<reflect-block>   ::= "reflect using GPT:" STRING
<event-block>     ::= "on event" STRING "as" IDENT ":" "respond using GPT:" STRING
<schedule-block>  ::= "every" NUMBER "s: recall" STRING

<var-assign>      ::= IDENT "=" <value>
<value>           ::= STRING | NUMBER | <list>
<list>            ::= "[" [<value> ("," <value>)*] "]"

IDENT             ::= letter (letter | digit | "_")*
STRING            ::= '"' .*? '"'
NUMBER            ::= integer or float literal




Lark Grammar (Python-ready):

from lark import Lark

aether_grammar = r"""
start: statement+

statement: agent_def | remember_block | forget_block

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





6. Execution Model & Semantics

Overview: AetherLang programs follow a Parse → Transform → Run lifecycle.

Parse → Lark parser constructs a parse tree from the .aether source.

Transform → Converts parse tree into Python dictionary capturing:

Agent name

Memory key–value store

Goal string

Behaviors (think, reflect, events, schedules)

Run → Interpreter:

Loads memory from memory/<agent>.json if exists; otherwise uses static memory block.

Starts background threads for scheduled recalls (every N s: recall "key").

Enters REPL (terminal) or GUI loop to process events and manual commands.

Event Handling

When a user triggers on event "...":

Formats the response template with memory values ({key}).

Calls GPT to generate the response.

Optionally accepts a GPT-proposed memory update (validated as JSON).

Schedules

every N s: recall "key" runs in a background thread without blocking REPL or GUI.

Scheduler prints memory key values (or goal if key absent).

Persistence

Automatic updates: Any memory-modifying command (remember, forget, event responses) immediately updates memory/<agent>.json.

Exit-triggered save: If no memory-modifying commands are typed, using exit will create memory.json with current agent state.

Runtime updates: remember / forget apply instantly; GPT updates merge only if valid JSON. Invalid updates are ignored.

Scheduled recalls run in background threads without blocking user input.





7. GPT Prompt Conventions

Reflect (manual or automatic):

Agent memory: <JSON memory>
Goal: <goal string>
Now: <reflection prompt>

Think (spontaneous generation):

Agent memory: <key: value, ...>
Think: <think prompt>

Respond (event-based):

Agent memory: <JSON memory>
<response-template-with-placeholders>

Memory Update (one-key JSON):

Here is the current memory: <memory>
Suggest ONE key-value update as JSON.
If no update is needed, return {}.

Practical Notes:

Pin GPT model and set temperature=0 for deterministic memory updates.

Always validate GPT output before merging into memory.

Manual reflect using gpt "..." in the REPL fully respects memory/goal state.





8. Memory, Persistence & Scheduling Semantics

Startup: Load memory/<agent>.json if it exists; otherwise use static memory: block.

Runtime updates:

remember / forget → apply instantly in memory.

GPT updates → applied only if valid JSON.


Persistence: Disk save happens only on REPL exit or GUI window close.

Scheduled recalls: Background threads periodically print memory key values without blocking user input.


This design ensures safe persistence, predictable updates, and time-native AI behavior.





9. Error messages & debugging tips

The AetherLang interpreter is designed to guide developers instead of failing silently.

Common Errors
⚠️ Invalid remember syntax. Use: remember "key" = "value"
⚠️ Please wrap the key in double quotes: forget "key"
🤖 No event handler for that input.

Success Confirmations
🧠 Remembered: <key> = <value>
🧠 Forgot: <key>
🧠 Memory updated: <update>
🧠 Memory saved to memory/<agent>.json (on exit)
👋 Exiting agent.

Debugging Workflow

Check syntax — are keys wrapped in double quotes?

Check persistence — type exit (REPL) or close GUI to save.

Check active agent — confirm the correct agent was loaded from examples/.

💡 Note:

memory/<agent>.json is created automatically when any memory-modifying command is typed, or when exit is 
used to terminate the session.

This ensures developers never lose memory updates and can safely reproduce agent states.





10. Interactive examples


MyAgent Example

1️⃣ Memory Updates & Automatic Persistence

Commands that modify memory automatically create or update the JSON file (memory/MyAgent.json). This includes commands like:

handle input …

remember "key" = "value"


Note: Commands like reflect using gpt … do not trigger memory updates.


![MyAgent Memory Update](docs/screenshots/myagent_memory_update.png)



2️⃣ Exit & Finalization


Explain: This screenshot shows the user typing exit. If no memory-modifying command was used before, exit 
will still create the memory file. This ensures every session can persist the agent state.


![MyAgent Exit](docs/screenshots/myagent_exit.png)



TutorBot Example


1️⃣ Memory Updates & Automatic Persistence

![TutorBot Memory Update](docs/screenshots/tutorbot_memory_update.png)


2️⃣ Exit & Session Finalization

[TutorBot Exit](docs/screenshots/tutorbot_exit.png)



HealthHelper Example


1️⃣ Memory Updates & Automatic Persistence

![HealthHelper Memory Update](docs/screenshots/healthhelper_memory_update.png)


2️⃣ Exit & Session Finalization

![HealthHelper Exit](docs/screenshots/healthhelper_exit.png)





11. Known Issues & Recommended Fixes

Add __main__ guard.

Unify grammar across lexer.py and interpreter.py.

Normalize input (e.g., lowercasing).

Ensure robust GPT JSON parsing.

Validate memory keys (avoid whitespace or reserved words).

Add unit tests for parser, transformer, scheduler, and persistence.







