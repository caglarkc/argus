import asyncio
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

argus_root = Path(__file__).parent.parent.parent
if str(argus_root) not in sys.path:
    sys.path.insert(0, str(argus_root))


class BFCLAdapter:
    """BFCLmessage - messageLLMClientmessage"""

    def __init__(self, llm_client: Any, model: str, name: str = "Argus-BFCL"):
        self.llm_client = llm_client
        self.model = model
        self.name = name

    def generate(self, prompt: str, functions: List[Dict[str, Any]]) -> str:
        try:
            return asyncio.run(self._async_generate(prompt, functions))
        except Exception as e:
            print(f"message: {e}")
            import traceback
            traceback.print_exc()
            return ""

    async def _async_generate(self, prompt: str, functions: List[Dict[str, Any]]) -> str:
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        tools = self._convert_functions_to_tools(functions)
        params = {"model": self.model, "tools": tools, "max_tokens": 1024}

        content = ""
        tool_calls = []

        stream = self.llm_client.astream_response(messages, **params)
        try:
            async for evt in stream:
                if evt.type == "output_text.delta":
                    content += evt.data
                elif evt.type == "tool_call.ready":
                    if isinstance(evt.data, list):
                        for tc in evt.data:
                            tool_calls.append({
                                "name": tc.get("name", ""),
                                "arguments": tc.get("arguments", {})
                            })
                elif evt.type == "completed":
                    break
                elif evt.type == "error":
                    print(f"LLMmessage: {evt.data}")
                    break
        finally:
            await stream.aclose()

        if tool_calls:
            return self._format_tool_calls(tool_calls)
        if content:
            return self._extract_function_from_response(content)
        return ""

    def _get_system_prompt(self) -> str:
        return "You are a helpful assistant. When given a function calling task, output the function call directly."

    def _convert_functions_to_tools(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tools = []
        for func in functions:
            tool = {
                "type": "function",
                "function": {
                    "name": func.get("name", ""),
                    "description": func.get("description", ""),
                    "parameters": func.get("parameters", {"type": "object", "properties": {}})
                }
            }
            tools.append(tool)
        return tools

    def _format_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> str:
        results = []
        for tc in tool_calls:
            name = tc.get("name", "")
            args = tc.get("arguments", {})
            if isinstance(args, dict):
                args_str = ", ".join(f"{k}={repr(v)}" for k, v in args.items())
            else:
                args_str = str(args)
            results.append(f"{name}({args_str})")
        return "\n".join(results)

    def _extract_function_from_response(self, response: str) -> str:
        response = response.strip()
        code_match = re.search(r'```(?:python)?\s*(.*?)\s*```', response, re.DOTALL)
        if code_match:
            code = code_match.group(1).strip()
            if re.match(r'^\w+\(.*\)$', code, re.DOTALL):
                return code
        func_match = re.search(r'(\w+)\s*\((.*?)\)', response, re.DOTALL)
        if func_match:
            return func_match.group(0)
        return response


def create_bfcl_adapter(llm_client: Any, model: str, name: Optional[str] = None) -> BFCLAdapter:
    adapter_name = name or "Argus-BFCL"
    return BFCLAdapter(llm_client=llm_client, model=model, name=adapter_name)

