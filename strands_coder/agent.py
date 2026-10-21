"""Local Strands coding agent whose LLM runs on Amazon Bedrock AgentCore Runtime.

  python agent.py                      # interactive REPL in current dir
  python agent.py -w ~/proj "add tests"  # one-shot
"""

import argparse
import os

from dotenv import load_dotenv
from strands import Agent

import tools
from agentcore_model import AgentCoreRuntimeModel

SYSTEM_PROMPT = (
    "You are a careful coding assistant working inside a local workspace. Explore with list_files/read_file "
    "before changing anything, prefer small edit_file changes over rewriting files, and verify your work by "
    "running tests or commands. Be concise."
)


def main() -> None:
    load_dotenv()
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", nargs="*")
    ap.add_argument("-w", "--workspace", default=".")
    ap.add_argument("-y", "--yes", action="store_true", help="auto-approve writes and commands")
    a = ap.parse_args()

    arn = os.environ.get("AGENTCORE_RUNTIME_ARN")
    if not arn:
        ap.error("set AGENTCORE_RUNTIME_ARN (see .env.example)")
    tools.set_root(a.workspace, a.yes)
    model = AgentCoreRuntimeModel(arn, region_name=os.environ.get("AWS_REGION"),
                                  qualifier=os.environ.get("AGENTCORE_QUALIFIER"))
    agent = Agent(model=model, tools=tools.TOOLS, system_prompt=SYSTEM_PROMPT)

    if a.prompt:
        agent(" ".join(a.prompt))
        return
    print(f"workspace: {tools.ROOT}  (ctrl-d to quit)")
    while True:
        try:
            q = input("\n> ").strip()
        except EOFError:
            break
        if q:
            agent(q)


if __name__ == "__main__":
    main()
