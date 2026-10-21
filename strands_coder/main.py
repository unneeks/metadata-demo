"""Strands coding agent as an AgentCore app.

  agentcore dev            # local server + UI, hot reload; the LLM is whatever your AgentCore/Bedrock config uses
  python main.py           # same app standalone on :8080

Invoke payload: {"prompt": "..."}. Conversation memory is kept per runtime session id.
Set CODER_WORKSPACE to the project to work on (default: current directory).
"""

import os

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel

import tools

SYSTEM_PROMPT = """You are an expert software engineer working in a local workspace through tools.
Workflow: explore (list_files, search, read_file) -> make minimal, targeted changes (edit_file; write_file for
new files) -> verify by running the project's tests/linters/build with run_command -> fix failures and repeat.
To test an app that keeps running, use start_process, check process_logs, exercise it (e.g. curl via
run_command), then stop_process. Never claim something works without having run it. Use git_diff to review
your changes before finishing. Be concise; end with a short summary of what changed and how you verified it."""

app = BedrockAgentCoreApp()
_agents: dict[str, Agent] = {}


def _model() -> BedrockModel:
    model_id = os.environ.get("BEDROCK_MODEL_ID")
    return BedrockModel(model_id=model_id) if model_id else BedrockModel()


def _agent(session_id: str) -> Agent:
    if session_id not in _agents:
        _agents[session_id] = Agent(model=_model(), tools=tools.TOOLS, system_prompt=SYSTEM_PROMPT,
                                    callback_handler=None)
    return _agents[session_id]


@app.entrypoint
async def invoke(payload, context=None):
    prompt = (payload or {}).get("prompt", "").strip()
    if not prompt:
        yield {"type": "error", "message": "payload needs a non-empty 'prompt'"}
        return
    agent = _agent(getattr(context, "session_id", None) or "default")
    seen: set[str] = set()
    try:
        async for ev in agent.stream_async(prompt):
            if "data" in ev:
                yield {"type": "text", "data": ev["data"]}
            elif (tu := ev.get("current_tool_use")) and tu.get("toolUseId") not in seen:
                seen.add(tu["toolUseId"])
                yield {"type": "tool", "name": tu.get("name")}
            elif (msg := ev.get("message")) and msg.get("role") == "user":
                for block in msg["content"]:
                    if "toolResult" in block:
                        text = "".join(c.get("text", "") for c in block["toolResult"]["content"])
                        yield {"type": "tool_result", "status": block["toolResult"]["status"], "text": text[:2000]}
    except Exception as e:  # surface model/credential errors in the UI instead of a bare 500
        yield {"type": "error", "message": f"{type(e).__name__}: {e}"}


if __name__ == "__main__":
    app.run()
