# strands_coder

A Strands coding agent that runs **locally** (tools read/edit files and run commands in your workspace)
while its **LLM runs on Amazon Bedrock AgentCore Runtime**.

```
local: Agent loop + tools ──(invoke_agent_runtime, SSE)──> AgentCore Runtime: model_proxy.py ──> Bedrock model
```

## 1. Deploy the model runtime
```bash
pip install -r requirements.txt
agentcore configure -e runtime/model_proxy.py -rf runtime/requirements.txt   # name it e.g. model_proxy
agentcore launch --env BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
```
The runtime's execution role needs `bedrock:InvokeModelWithResponseStream`. Copy the runtime ARN from the output.

## 2. Run the agent locally
```bash
cp .env.example .env   # set AGENTCORE_RUNTIME_ARN, AWS_REGION
python agent.py -w /path/to/project            # REPL
python agent.py -w /path/to/project -y "fix the failing test"   # one-shot, auto-approve
```
Your local AWS credentials need `bedrock-agentcore:InvokeAgentRuntime` on the ARN.

Writes, edits and shell commands ask for confirmation unless `-y`; file tools are confined to the workspace
(the shell tool is not a sandbox). Images/documents in messages are not supported by the proxy protocol.
