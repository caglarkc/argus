from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Generic, TypeVar, Literal

class LLM_Events:
    REQUEST_STARTED       = "request.started"
    ASSISTANT_DELTA       = "assistant.delta"
    ASSISTANT_FINISHED    = "assistant.finished"
    TOOL_CALL_DELTA       = "tool_call.delta"
    TOOL_CALL_READY       = "tool_call.ready"
    REASONING_DELTA       = "reasoning.delta"
    REASONING_FINISHED    = "reasoning.finished"
    TOKEN_USAGE           = "metrics.token_usage"
    RESPONSE_FINISHED     = "response.finished"
    ERROR                 = "error"


EventType = Literal[
        "request.started",         #x message 
        "assistant.delta",         #  message
        "assistant.finished",      #x message
        "tool_call.delta",         #x message
        "tool_call.ready",         #  message,message
        "reasoning.delta",         #  message
        "reasoning.finished",      #x message/message
        "metrics.token_usage",     #  message
        "web_search_begin",
        "response.finished",       #  message
        "error",                   #  message
        ]

T = TypeVar("T")

@dataclass
class ResponseEvent(Generic[T]):
    type: EventType
    data: Optional[T] = None

    @staticmethod
    def request_started(meta: Optional[Dict[str, Any]] = None) -> ResponseEvent[Dict[str, Any]]:
        return ResponseEvent("request.started", meta or {})

    @staticmethod
    def error_event(message: str, extra: Optional[Dict[str, Any]] = None) -> ResponseEvent[Dict[str, Any]]:
        payload = {"message": message, **(extra or {})}
        return ResponseEvent("error", payload)

    @staticmethod
    def assistant_delta(delta: str) -> ResponseEvent:
        return ResponseEvent("assistant.delta", delta)

    @staticmethod
    def tool_call_delta(call_id: str, name: str | None, arguments: str, kind: str) -> ResponseEvent[Dict[str, Any]]:
        # kind: "function" | "custom"
        payload = {"call_id": call_id, "name": name, "arguments": arguments, "type": kind}
        return ResponseEvent("tool_call.delta", payload)
    
    @staticmethod
    def tool_call_ready(item) -> ResponseEvent[Dict[str, Any]]:
        return ResponseEvent("tool_call.ready", item)

    @staticmethod
    def reasoning_delta(delta: str) -> ResponseEvent[str]:
        return ResponseEvent("reasoning.delta", delta)

    @staticmethod
    def reasoning_finished(summary: str) -> ResponseEvent:
        return ResponseEvent("reasoning.finished", summary)

    @staticmethod
    def web_search_begin(call_id: str)-> ResponseEvent[Dict[str, Any]]:
        return ResponseEvent("web_search_begin", {"call_id": call_id})

    @staticmethod
    def token_usage(usage: Dict[str, int]) -> ResponseEvent[Dict[str, Any]]:
        return ResponseEvent("metrics.token_usage", usage)

    @staticmethod
    def response_finished(resp: Any = None) -> ResponseEvent[Dict[str, Any]]:
        return ResponseEvent("response.finished", resp) 

    @staticmethod
    def error(message: str, extra: Optional[Dict[str, Any]] = None) -> ResponseEvent[Dict[str, Any]]:
        payload = {"message": message, **(extra or {})}
        return ResponseEvent("error", payload)
