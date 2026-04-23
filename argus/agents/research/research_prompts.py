from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


query_writer_instructions = """Your goal is to generate sophisticated and diverse web search queries. These queries are intended for an advanced automated web research tool capable of analyzing complex results, following links, and synthesizing information.

Instructions:
- Always prefer a single search query, only add another query if the original question requests multiple aspects or elements and one query is not enough.
- Each query should focus on one specific aspect of the original question.
- Don't produce more than {number_queries} queries.
- Queries should be diverse, if the topic is broad, generate more than 1 query.
- Don't generate multiple similar queries, 1 is enough.
- Query should ensure that the most current information is gathered. The current date is {current_date}.

Format: 
- Format your response as a JSON object with ALL two of these exact keys:
   - "rationale": Brief explanation of why these queries are relevant
   - "query": A list of search queries

Example:

Topic: What revenue grew more last year apple stock or the number of people buying an iphone
```json
{{
    "rationale": "To answer this comparative growth question accurately, we need specific data points on Apple's stock performance and iPhone sales metrics. These queries target the precise financial information needed: company revenue trends, product-specific unit sales figures, and stock price movement over the same fiscal period for direct comparison.",
    "query": ["Apple total revenue growth fiscal year 2024", "iPhone unit sales growth fiscal year 2024", "Apple stock price growth fiscal year 2024"],
}}
```

Context: {research_topic}"""


web_search_executor_instructions = """Conduct targeted web searches to gather the most recent, credible information on "{research_topic}".

Instructions:
- Query should ensure that the most current information is gathered. The current date is {current_date}.
- You MUST use the web_search tool for EACH of the provided search queries below.
- Do NOT combine or merge the queries - search each one individually.
- Each query targets a specific aspect of the research topic and should be searched separately.
- Identify the most relevant URLs from search results for detailed content fetching.
- Only include the information found in the search results, don't make up any information.

Search Queries to Execute:
{research_topic}

IMPORTANT: Call the web_search tool once for each query listed above. Do not skip any queries.
"""

web_fetch_executor_instructions = """Fetch detailed content from the provided URLs to gather in-depth information on "{research_topic}".

Instructions:
- Use web_fetch tool to read detailed content from the provided web_search results,which contained website URLs.
- Extract key information that helps answer the research topic.
- Track the source URL for each piece of information.
- Only include the information found in the web pages, don't make up any information.

web_search results to fetch:
{web_search_results}

Research Topic:
{research_topic}

"""

summary_generator_instructions = """Synthesize the provided search results into a verifiable text artifact.

Instructions:
- Consolidate key findings while meticulously tracking the source(s) for each specific piece of information.
- The output should be a well-written summary or report based on the search findings.
- Only include the information found in the search results, don't make up any information.

Search Results:
{search_results}

Research Topic:
{research_topic}
"""

reflection_instructions = """You are an expert research assistant analyzing summaries about "{research_topic}".

Instructions:
- Identify knowledge gaps or areas that need deeper exploration and generate a follow-up query. (1 or multiple).
- If provided summaries are sufficient to answer the user's question, don't generate a follow-up query.
- If there is a knowledge gap, generate a follow-up query that would help expand your understanding.
- Focus on technical details, implementation specifics, or emerging trends that weren't fully covered.

Requirements:
- Ensure the follow-up query is self-contained and includes necessary context for web search.

Output Format:
- Format your response as a JSON object with these exact keys:
   - "is_sufficient": true or false
   - "knowledge_gap": Describe what information is missing or needs clarification
   - "follow_up_queries": Write a specific question to address this gap

Example:
```json
{{
    "is_sufficient": true, // or false
    "knowledge_gap": "The summary lacks information about performance metrics and benchmarks", // "" if is_sufficient is true
    "follow_up_queries": ["What are typical performance benchmarks and metrics used to evaluate [specific technology]?"] // [] if is_sufficient is true
}}
```

Reflect carefully on the Summaries to identify knowledge gaps and produce a follow-up query. Then, produce your output following this JSON format:

Summaries:
{summaries}
"""

answer_instructions = """Generate a high-quality answer to the user's question based on the provided summaries.

Instructions:
- The current date is {current_date}.
- You are the final step of a multi-step research process, don't mention that you are the final step. 
- You have access to all the information gathered from the previous steps.
- You have access to the user's question.
- Generate a high-quality answer to the user's question based on the provided summaries and the user's question.
- Include the sources you used from the Summaries in the answer correctly, use markdown format (e.g. [apnews](https://vertexaisearch.cloud.google.com/id/1-0)). THIS IS A MUST.

User Context:
- {research_topic}

Summaries:
{summaries}"""
