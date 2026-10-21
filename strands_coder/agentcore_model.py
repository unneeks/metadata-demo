"""Strands model provider that delegates inference to an Amazon Bedrock AgentCore Runtime.

The agent loop and tools run locally; each model turn is POSTed to a deployed
AgentCore Runtime (see runtime/model_proxy.py) which streams back Strands
stream events (Bedrock Converse-style dicts).
"""

import asyncio
import json
import uuid
from typing import Any, AsyncGenerator, AsyncIterable, Optional, Type, TypeVar

import boto3
from pydantic import BaseModel
from strands.models import Model

T = TypeVar("T", bound=BaseModel)

_DONE = object()


def _json_default(o: Any) -> Any:
    if isinstance(o, (bytes, bytearray)):
        raise TypeError("binary content (images/documents) is not supported by AgentCoreRuntimeModel")
    return str(o)


class AgentCoreRuntimeModel(Model):
    def __init__(self, agent_runtime_arn: str, region_name: Optional[str] = None,
                 qualifier: Optional[str] = None, session_id: Optional[str] = None,
                 client: Any = None, **model_config: Any) -> None:
        self.config: dict[str, Any] = {"agent_runtime_arn": agent_runtime_arn, **model_config}
        self.qualifier = qualifier
        # AgentCore requires a runtime session id of at least 33 characters.
        self.session_id = session_id or f"strands-coder-{uuid.uuid4()}"
        self.client = client or boto3.client("bedrock-agentcore", region_name=region_name)

    def update_config(self, **model_config: Any) -> None:
        self.config.update(model_config)

    def get_config(self) -> dict[str, Any]:
        return self.config

    def _lines(self, payload: dict[str, Any]):
        kwargs: dict[str, Any] = dict(
            agentRuntimeArn=self.config["agent_runtime_arn"],
            runtimeSessionId=self.session_id,
            contentType="application/json",
            accept="text/event-stream",
            payload=json.dumps(payload, default=_json_default).encode(),
        )
        if self.qualifier:
            kwargs["qualifier"] = self.qualifier
        resp = self.client.invoke_agent_runtime(**kwargs)
        body = resp["response"]
        for raw in body.iter_lines():
            line = raw.decode() if isinstance(raw, bytes) else raw
            if line.startswith("data:"):
                yield line[5:].strip()
            elif line.strip() and not line.startswith(("event:", "id:", ":")):
                yield line.strip()  # plain JSON-lines fallback

    async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs: Any
                     ) -> AsyncIterable[dict[str, Any]]:
        payload = {
            "messages": messages,
            "tool_specs": tool_specs,
            "system_prompt": system_prompt,
            "tool_choice": kwargs.get("tool_choice"),
            "params": {k: v for k, v in self.config.items() if k != "agent_runtime_arn"},
        }
        it = self._lines(payload)
        loop = asyncio.get_running_loop()
        while True:
            line = await loop.run_in_executor(None, next, it, _DONE)
            if line is _DONE:
                return
            data = json.loads(line)
            if isinstance(data, str):  # double-encoded by some SDK versions
                data = json.loads(data)
            if "error" in data and len(data) <= 2:
                raise RuntimeError(f"AgentCore runtime error: {data['error']}")
            yield data

    async def structured_output(self, output_model: Type[T], prompt, system_prompt=None, **kwargs: Any
                                ) -> AsyncGenerator[dict[str, Any], None]:
        raise NotImplementedError("structured_output is not supported by AgentCoreRuntimeModel")
        yield  # pragma: no cover
