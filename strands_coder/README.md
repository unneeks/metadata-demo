# strands_coder

A Strands coding agent packaged as an AgentCore app. Run it with `agentcore dev` (local server + UI, hot reload);
it uses the Bedrock model from your AgentCore/AWS configuration and edits and tests code on your machine.

## Run
```bash
pip install -r requirements.txt
export CODER_WORKSPACE=/path/to/project     # what the agent may edit (default: cwd)
# optional: export BEDROCK_MODEL_ID=...     # otherwise the Strands/Bedrock default model is used
agentcore dev                                # or: python main.py
```
Without the UI:
```bash
curl -N localhost:8080/invocations -H 'content-type: application/json' \
  -d '{"prompt":"run the tests and fix any failures"}'
```
The stream emits `{"type": "text" | "tool" | "tool_result" | "error", ...}` events. Conversation state is kept
per session id (`X-Amzn-Bedrock-AgentCore-Runtime-Session-Id` header).

## Tools
`list_files`, `read_file` (line ranges), `search` (regex), `write_file`, `edit_file` (unique-match, returns diff),
`run_command` (timeout, process-group kill, output truncation), `git_diff`, and `start_process` /
`process_logs` / `stop_process` for running and checking servers.

## Safety
File tools are confined to `CODER_WORKSPACE`. Shell commands are **not sandboxed** (a denylist blocks `sudo`,
`rm -rf /`, curl|sh, force-push, etc.) — there is no interactive approval in server mode, so use a git branch or
container, or set `CODER_READONLY=1` to disable writes and commands.
