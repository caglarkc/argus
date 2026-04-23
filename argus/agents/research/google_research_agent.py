from typing import Dict, Any, List, AsyncGenerator, Optional
from argus.agents.base_agent import BaseAgent
from argus.llm.llm_basics import LLMMessage, LLMResponse
from argus.llm.llm_basics import ToolCallResult
from argus.llm.llm_client import LLMClient
from argus.hooks.manager import HookManager
from argus.agents.research.research_prompts import (get_current_date,
    query_writer_instructions,
    web_search_executor_instructions,
    web_fetch_executor_instructions,
    summary_generator_instructions,
    reflection_instructions,
    answer_instructions)
import json
import re


def _extract_json(content: str) -> str:
    """message ```json``` message"""
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
    if json_match:
        return json_match.group(1)
    return content


class GeminiResearchDemo(BaseAgent):
    """Research agent specialized for multi-step research tasks."""
    
    def __init__(self, config, tool_mgr, hook_mgr: HookManager):
        super().__init__(config, tool_mgr, hook_mgr)

        self.type = "GeminiResearchDemo"

        # Create LLM client using active model config
        self.llm_client = LLMClient(config.active_model)
        
        # Research state
        self.research_state = {
            "topic": "",
            "queries": [],
            "search_results": [],
            "summaries": [],
            "current_step": "query_generation",
            "iteration": 0
        }
        # Get available tools for research agent
        self.available_tools = [tool.build("research") for tool in self.tool_mgr.list_for_provider("research")]
        self.max_iterations = 3
    
    def _build_system_prompt(self) -> str:
        """message"""
        current_date = get_current_date()
        
        return f"""You are an expert research assistant conducting comprehensive research. Today's date is {current_date}.

You have access to these tools:
- web_search: Search the web for information
- web_fetch: Fetch and read content from specific URLs  
- write_file: Save research findings and reports
- read_file: Read previously saved research files

Follow the research process step by step and use the appropriate prompts for each stage."""

    def _get_query_writer_prompt(self, topic: str, number_queries: int = 3) -> str:
        """message"""
        return query_writer_instructions.format(current_date=get_current_date(),
            research_topic=topic,
            number_queries=number_queries)

    def _get_web_search_executor_prompt(self, queries: List[str]) -> str:
        """message"""
        # message
        queries_text = "\n".join([f"- {query}" for query in queries])
        return web_search_executor_instructions.format(current_date=get_current_date(),
            research_topic=queries_text)

    def _get_web_fetch_executor_prompt(self, queries: List[str], web_search_results: List[ToolCallResult]) -> str:
        """message"""
        queries_text = "\n".join([f"- {query}" for query in queries])
        return web_fetch_executor_instructions.format(current_date=get_current_date(),
            web_search_results="\n".join([result for result in web_search_results]),
            research_topic=queries_text)
    def _get_summary_generator_prompt(self, topic: str, search_results: Optional[List[Any]] = None) -> str:
        """message"""
        # message,message
        formatted_results = []
        for query_result in search_results:
            if isinstance(query_result, dict) and 'results' in query_result:
                query = query_result.get('query', '')
                formatted_results.append(f"message: {query}")
                
                for i, result in enumerate(query_result['results'], 1):
                    title = result.get('title', '')
                    url = result.get('url', '')
                    snippet = result.get('snippet', '')
                    web_content = result.get('web_content', '')
                    
                    formatted_results.append(f"{i}. message: {title}")
                    formatted_results.append(f"   URL: {url}")
                    formatted_results.append(f"   message: {snippet}")
                    
                    if web_content:
                        # message,message
                        content_preview = web_content[:5000] + "..." if len(web_content) > 5000 else web_content
                        formatted_results.append(f"   message: {content_preview}")
                    
                    formatted_results.append("")  # message
        
        results_text = "\n".join(formatted_results)
        
        return summary_generator_instructions.format(research_topic=topic,
            search_results=results_text)

    def _get_reflection_prompt(self, topic: str) -> str:
        """message"""
        summaries = "\n".join(self.research_state.get("summaries", []))
        
        return reflection_instructions.format(research_topic=topic,
            summaries=summaries if summaries else "No summaries available yet. This indicates we need to conduct initial research.")

    def _get_answer_prompt(self, topic: str) -> str:
        """message"""
        summaries = "\n".join(self.research_state.get("summaries", []))
        
        return answer_instructions.format(current_date=get_current_date(),
            research_topic=topic,
            summaries=summaries)

    # TODO:
    async def run(self, user_message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Run research agent with multi-step research workflow."""
        
        # message
        self.research_state["topic"] = user_message
        self.research_state["iteration"] = 0
        yield {"type": "user_message", "data": {"message": user_message}}
        
        # Start trajectory recording
        self.trajectory_recorder.start_recording(task=user_message,
            provider=self.config.active_model.provider or "openai",
            model=self.config.active_model.model,
            max_steps=None)
        self.conversation_history.append(LLMMessage(role="user", content=user_message))
        
        # 1. message
        async for queries in self.generate_queries(user_message):
            yield queries

        # 2. message
        async for search in self.web_search(self.research_state['queries']):
            yield search

        # Google LangGraph message
        while True:
            try:
                self.research_state["iteration"] += 1
                # 3. message
                reflection_prompt = self._get_reflection_prompt(self.research_state["topic"])
                reflection_response = await self.llm_client.generate_response([LLMMessage(role="user", content=reflection_prompt)])
                
                # messagereflectionmessage
                self.conversation_history.append(LLMMessage(role="assistant", 
                    content=reflection_response.content))

                # messageJSONmessage
                json_content = _extract_json(reflection_response.content)
                try:
                    reflection_data = json.loads(json_content)
                except json.JSONDecodeError as e:
                    yield {"type": "error", "data": {"error": f"Failed to parse reflection response JSON: {str(e)}. Content: {reflection_response.content}"}}
                    break
                
                is_sufficient = reflection_data.get("is_sufficient", False)
                
                # 4.message,message
                if is_sufficient or self.research_state['iteration']> self.max_iterations:
                    break
                else:
                    # messagefollow_up_queriesmessage
                    follow_up_queries = reflection_data.get("follow_up_queries", [])
                    if follow_up_queries:
                        # message
                        self.research_state["queries"] = follow_up_queries
                        async for search in self.web_search(follow_up_queries):
                            yield search

            except Exception as e:
                yield {"type": "error", "data": {"error": str(e)}}
                break
        
        # 5. message
        accumulated_content = ""
        final_response = None
        final_prompt = self._get_answer_prompt(user_message)
        stream_generator = await self.llm_client.generate_response([LLMMessage(role="user", content=final_prompt)],
            stream=True)
        # message
        yield {"type": "final_answer_start", "data": {}}
        async for chunk in stream_generator:
            if chunk.content:
                current_content = chunk.content
                if current_content!= accumulated_content:
                    new_content = current_content[len(accumulated_content):]
                    if new_content:
                        yield {"type": "final_answer_chunk", "data": {"content": new_content}}
                    accumulated_content = current_content
            final_response = chunk
        if final_response:
            self.conversation_history.append(LLMMessage(role="assistant", content=final_response.content))
            self.trajectory_recorder.record_llm_interaction(messages=self.conversation_history,
                response=LLMResponse(content=final_response.content,
                    model=self.config.active_model.model,
                    usage=final_response.usage,
                    tool_calls=None,),
                provider=self.config.active_model.provider or "openai",
                model="answer_generator",
                current_task=self.research_state['topic'],)
    
    async def generate_queries(self,user_message: str):
        query_prompt = self._get_query_writer_prompt(user_message)
        query_response = await self.llm_client.generate_response([LLMMessage(role="user", content=query_prompt)],stream=False)

        json_content = _extract_json(query_response.content)
        try:
            query_data = json.loads(json_content)
        except json.JSONDecodeError as e:
            yield {"type": "error", "data": {"error": f"Failed to parse reflection response JSON: {str(e)}. Content: {query_response.content}"}}
            return
        queries = query_data.get("query", [])

        yield {"type": "query", "data":{"queries": queries}}

        # message
        self.research_state["queries"] = queries
        self.conversation_history.append(LLMMessage(role="assistant",content=json_content))
        
        self.trajectory_recorder.record_llm_interaction(messages= self.conversation_history,
            response=LLMResponse(content=json_content,
                model=self.config.active_model.model,
                usage=query_response.usage,
                tool_calls=None,),
            provider=self.config.active_model.provider or "openai",
            model="query_generator",
            current_task=user_message,)
        
    async def web_search(self,query:List[str]):
        """message,messageURLs,messageURLmessage,message"""

        # 1. messageURLs
        search_prompt = self._get_web_search_executor_prompt(query)
        search_response = await self.llm_client.generate_response(messages=[LLMMessage(role="user", content=search_prompt)],
            tools=self.available_tools)
        search_results = []
        str_search_results = []
        if search_response.content:
            yield {"type": "search", "data": {"content": search_response.content}}
            self.conversation_history.append(LLMMessage(role="assistant", content=search_response.content))
        
        if search_response.tool_calls:
            # message
            for tool_call in search_response.tool_calls:
                yield {"type": "tool_call", "data": {"tool_call": tool_call}}

            async for result in self._process_tool_calls(search_response.tool_calls):
                yield result
                data = result.get("data")
                if data and "metadata" in data and data["metadata"]:
                    search_results.append(data["metadata"])
                if data and "result" in data and data["result"]:
                    str_search_results.append(data["result"])
                # message
                tool_msg = LLMMessage(role="tool",
                    content=data["result"],
                    tool_call_id=tool_call.call_id)
                self.conversation_history.append(tool_msg)
        
        self.trajectory_recorder.record_llm_interaction(messages= self.conversation_history,
            response=LLMResponse(content=search_response.content,
                model=self.config.active_model.model,
                usage=search_response.usage,
                tool_calls=search_response.tool_calls,),
            provider=self.config.active_model.provider or "openai",
            model="web_searcher_generator",
            current_task=self.research_state['topic'],)

        # 2. message
        if search_results:
            fetch_prompt = self._get_web_fetch_executor_prompt(self.research_state['queries'], str_search_results)
            fetch_response = await self.llm_client.generate_response([LLMMessage(role="user", content=fetch_prompt)],
                tools=self.available_tools)
            fetch_results = {}
            
            if fetch_response.content:
                yield {"type": "fetch", "data": {"content": fetch_response.content}}
                self.conversation_history.append(LLMMessage(role="assistant", content=fetch_response.content))
            
            if fetch_response.tool_calls:
                # message
                for tool_call in fetch_response.tool_calls:
                    yield {"type": "tool_call", "data": {"tool_call": tool_call}}
                    
                async for result in self._process_tool_calls(fetch_response.tool_calls):
                    yield result
                    data = result.get('data')
                    # messageURLmessage
                    if (data and 'result' in data and data['result'] and 
                        'call_id' in data):
                        # messagetool_callsmessageURL
                        for tool_call in fetch_response.tool_calls:
                            if tool_call.call_id == data['call_id']:
                                url = tool_call.arguments.get('url')
                                if url:
                                    fetch_results[url] = data['result']
                                    # message
                                    tool_msg = LLMMessage(role="tool",
                                        content=data['result'],
                                        tool_call_id=tool_call.call_id)
                                    self.conversation_history.append(tool_msg)
                                break
            
                # message
                for query_dict in search_results:
                    if isinstance(query_dict, dict):
                        query_result = query_dict.get('results')
                        for search_result in query_result:
                            if isinstance(search_result, dict):
                                url = search_result.get('url')
                                if url and url in fetch_results:
                                    search_result['web_content'] = fetch_results[url]
            else:
                yield {"type": "fetch", "data": {"content": "No search results to fetch content from."}}
                self.research_state['search_results'].append(search_results)
                self.trajectory_recorder.record_llm_interaction(messages= self.conversation_history,
                    response=LLMResponse(content="No search results to fetch content from.",
                        model=self.config.active_model.model,
                        usage=None,
                        tool_calls=None,),
                    provider=self.config.active_model.provider or "openai",
                    model="web_fetcher_generator",
                    current_task=self.research_state['topic'],)
                return
        
        self.research_state['search_results'].append(search_results)
        self.trajectory_recorder.record_llm_interaction(messages= self.conversation_history,
            response=LLMResponse(content=fetch_response.content,
                model=self.config.active_model.model,
                usage=search_response.usage,
                tool_calls=fetch_response.tool_calls,),
            provider=self.config.active_model.provider or "openai",
            model="web_fetcher_generator",
            current_task=self.research_state['topic'],)
        # 3. message
        summary_prompt = self._get_summary_generator_prompt(self.research_state['topic'], search_results)
        
        accumulated_content = ""
        final_response = None
        
        yield {"type": "summary_start", "data": {}}
        stream_generator = await self.llm_client.generate_response(messages=[LLMMessage(role="user", content=summary_prompt)], 
            stream=True)
        
        async for summary_response_chunk in stream_generator:
            # message
            if summary_response_chunk.content:
                current_content = summary_response_chunk.content
                if current_content!= accumulated_content:
                    new_content = current_content[len(accumulated_content):]
                    if new_content:
                        yield {"type": "summary_chunk", "data": {"content": new_content}}
                    accumulated_content = current_content
            final_response = summary_response_chunk

        # message
        if final_response:
            self.conversation_history.append(LLMMessage(role="assistant", content=final_response.content))
            self.trajectory_recorder.record_llm_interaction(messages=self.conversation_history,
                response=LLMResponse(content=final_response.content,
                    model=self.config.active_model.model,
                    usage=final_response.usage,
                    tool_calls=None,),
                provider=self.config.active_model.provider or "openai",
                model="summary_generator",
                current_task=self.research_state['topic'],)
            
            # message
            if isinstance(self.research_state["summaries"], list):
                self.research_state["summaries"].append(final_response.content)
            else:
                self.research_state["summaries"] = [final_response.content]
    async def _process_tool_calls(self, tool_calls):
        """message"""
        for tool_call in tool_calls:
            try:
                # message
                tool = self.tool_mgr.get_tool(tool_call.name)
                if not tool:
                    yield {"type": "error", "data": {"error": f"Tool not found: {tool_call.name}"}}
                    continue
                
                # message
                result = await tool.execute(**tool_call.arguments)
                
                yield {"type": "tool_result", "data": {
                    "call_id": tool_call.call_id,
                    "name": tool_call.name,
                    "metadata": getattr(result, 'metadata', None),
                    "result": getattr(result, 'result', None),
                    "url": getattr(result, 'url', None),
                    "success": getattr(result, 'success', True),
                    "error": getattr(result, 'error', None)
                }}
                
                # message
                content = ""
                if hasattr(result, 'result') and result.result:
                    content = str(result.result)
                elif hasattr(result, 'error') and result.error:
                    content = f"Error: {result.error}"
                else:
                    content = str(result)
                
                self.conversation_history.append(LLMMessage(role="tool",
                    content=content,
                    tool_call_id=tool_call.call_id))
                
            except Exception as e:
                yield {"type": "error", "data": {"error": f"Tool execution failed for {tool_call.name}: {str(e)}"}}

    def get_enabled_tools(self) -> List[str]:
        """Return list of enabled tool names for ResearchAgent."""
        return [
            'web_search',
            'web_fetch', 
            'write_file',
            'read_file'
        ]
    
