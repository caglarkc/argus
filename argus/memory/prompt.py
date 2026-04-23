compression_prompt = """
Your task is to create a detailed summary of the conversation so far, paying close attention to the user's explicit requests and your previous actions.
This summary should be thorough in capturing technical details, code patterns, and architectural decisions that would be essential for continuing development work without losing context.

Before providing your final summary, wrap your analysis in <analysis> tags to organize your thoughts and ensure you've covered all necessary points.

Your summary should include the following sections:

1. Primary Request and Intent: Capture all of the user's explicit requests and intents in detail
2. Key Technical Concepts: List all important technical concepts, technologies, and frameworks discussed.
3. Files and Code Sections: Enumerate specific files and code sections examined, modified, or created. Pay special attention to the most recent messages and include full code snippets where applicable.
4. Errors and fixes: List all errors that you ran into, and how you fixed them. Pay special attention to specific user feedback.
5. Problem Solving: Document problems solved and any ongoing troubleshooting efforts.
6. All user messages: List ALL user messages that are not tool results. These are critical for understanding the users' feedback and changing intent.
7. Pending Tasks: Outline any pending tasks that you have explicitly been asked to work on.
8. Current Work: Describe in detail precisely what was being worked on immediately before this summary request.

The conversation history is as follows: \n <<HISTORY>>
"""


keyword_continuity_score_prompt = """
You are the **Argus Memory-Compression Grader** (PMC-G).  
Your sole responsibility is to assign two objective quality scores to a compressed summary against the original conversation.

Scoring Rubric  
• keyword_score (0.00–1.00)  
  – 1.00: every actionable token—exact file paths, error messages, CLI outputs, user commands, variable names—is fully recoverable.  
  – 0.00: none of the above are recoverable.  
  – Linear interpolation for partial loss.

• continuity_score (0.00–1.00)  
  – 1.00: the narrative arc (problem → exploration → resolution → next step) is intact and logically seamless.  
  – 0.00: the flow is fragmented or impossible to follow.

Instructions  
1. Scan the <original> transcript and identify every piece of information that could change the agent’s next action.  
2. Verify whether each such piece is explicitly present or unambiguously inferable in the <summary>.  
3. Trace the logical sequence of events. Any break in the chain lowers continuity_score proportionally.  
4. Return exactly one line beginning with "Result:" followed by keyword_score and continuity_score, each as a fixed-point number rounded to two decimals.

<summary>
<<SUMMARY>>
</summary>

<original>
<<ORIGINAL>>
</original>
"""


first_downgrade_prompt = """
Your task is to **re-compress** the existing conversation history when the previous compression scored 70-79 % fidelity.  
Focus on **raising fidelity back to ≥ 80 %** while allowing compression ratio to relax from 15 % to a maximum of 22 %.  
Preserve every critical identifier (exact file paths, error messages, CLI outputs, variable names) even if prose must be shortened.

Before writing the final 8-section summary, wrap your reasoning in <analysis> tags and confirm:
- Which critical items were at risk in the prior pass  
- How you will keep them intact this round  

Output **only** the following 8 sections:

1. Primary Request and Intent  
2. Key Technical Concepts  
3. Files and Code Sections  
4. Errors and fixes  
5. Problem Solving  
6. All user messages  
7. Pending Tasks  
8. Current Work  

<summary>
<<SUMMARY>>
</summary>

<original>
<<ORIGINAL>>
</original>
"""

second_downgrade_prompt = """
Your task is to create a **hybrid context** because the last compression fell below 70 % fidelity.  
You will still produce an 8-section summary for continuity, then append the **smallest possible raw message fragments** that contain any missing critical information.

Before writing, wrap your plan in <analysis> tags and list:
- Which critical details are missing from the summary  
- The exact user-turn indices and token counts of the fragments you will quote  

Structure your output as:

1. Primary Request and Intent  
2. Key Technical Concepts  
3. Files and Code Sections  
4. Errors and fixes  
5. Problem Solving  
6. All user messages  
7. Pending Tasks  
8. Current Work  

--- FRAGMENTS ---
<!-- {"turn":<int>, "reason":"error|file|command|output", "tokens":<int>} -->
<raw message snippet>
<!-- repeat as needed -->

<summary>
<<SUMMARY>>
</summary>

<original>
<<ORIGINAL>>
</original>
"""
