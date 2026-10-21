"""AgentCore Runtime app that serves LLM inference for the local Strands agent.

Deploy with `agentcore configure -e runtime/model_proxy.py` then `agentcore launch`.
Streams Strands stream events (as SSE) from a Bedrock model.
"""

import os

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.models import BedrockModel

app = BedrockAgentCoreApp()
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")


@app.entrypoint
async def invoke(payload, context=None):
    params = payload.get("params") or {}
    model = BedrockModel(model_id=params.get("model_id", MODEL_ID),
                         **{k: v for k, v in params.items() if k in ("temperature", "max_tokens", "top_p")})
    kwargs = {"tool_choice": payload["tool_choice"]} if payload.get("tool_choice") else {}
    async for event in model.stream(payload["messages"], payload.get("tool_specs"),
                                    payload.get("system_prompt"), **kwargs):
        yield event


if __name__ == "__main__":
    app.run()
