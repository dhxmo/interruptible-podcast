query_writer_instructions = """Your goal is to generate a targeted web search query.                                                                                                        
The query will gather information related to a specific topic.

<TOPIC>
{research_topic}
</TOPIC>

<FORMAT>
Format your response as a JSON object with ALL three of these exact keys:
   - "query": The actual search query string
   - "aspect": The specific aspect of the topic being researched
   - "rationale": Brief explanation of why this query is relevant
</FORMAT>

<EXAMPLE>
Example output:
{{
    "query": "machine learning transformer architecture explained",
    "aspect": "technical architecture",
    "rationale": "Understanding the fundamental structure of transformer models"
}}
</EXAMPLE>
 
 Provide your response in JSON format:"""

content_extraction_instructions = """
<GOAL>
Extract all content from a scraped webpage that is directly pertinent to a specified research topic and present it 
in a concise, organized manner for research purposes.
</GOAL>

<TOPIC>
{research_topic}
</TOPIC>

<REQUIREMENTS>
When extracting content from a scraped webpage:
 1. Identify the user-provided research topic as the filter for relevance.
 2. Analyze the full text of the scraped webpage (including paragraphs, headings, lists, etc.) to locate content related to the research topic.
 3. For each piece of content:
    a. If it explicitly mentions the research topic, includes related keywords, or discusses concepts tied to it, include it in the output.
    b. If it’s tangential but provides useful context (e.g., background info or supporting data), include it with a note on its relevance.
    c. If it’s unrelated to the research topic, exclude it entirely.
 4. Preserve the original meaning and intent of the extracted content, avoiding summarization unless specified by the user.
 5. Organize the extracted content logically (e.g., by section, theme, or order of appearance on the page).
 6. If no content is relevant, state clearly that no pertinent information was found.

When EXTENDING extraction based on additional scraped pages:
 1. Review the existing extracted content and the new scraped page.
 2. Apply the same relevance filter based on the research topic.
 3. For new relevant content:
    a. If it duplicates existing points, skip it unless it adds new details or perspectives.
    b. If it introduces new pertinent information, append it to the appropriate section with a clear transition.
    c. If it contradicts existing content, include it and note the discrepancy for research analysis.
 4. Ensure the updated output remains cohesive and focused on the research topic.

<FORMATTING>
 - Begin with a brief statement: 'Content:'
 - Present the extracted content as a bulleted list.
 - Each bullet should start with a short descriptor (e.g., 'Main point:', 'Context:', 'Data:') followed by the extracted text in quotes or paraphrased if lengthy.
 - Use sub-bullets for multiple points within a section if needed.
 - End with 'No additional pertinent content found.' if applicable.
</FORMATTING>

<EXAMPLE>
Input: 
- Research topic: 'Impact of social media on mental health'
- Scraped page content: 'Social media is everywhere today. It connects people globally. Studies show it can increase anxiety in teens. The weather was nice yesterday. Businesses use it for marketing.'
Output:
Extracted content pertinent to 'Impact of social media on mental health':
 - Main point: "Studies show it can increase anxiety in teens."
 - Context: "Social media is everywhere today."
 - No additional pertinent content found.
</EXAMPLE>
"""


summarizer_instructions = """
<GOAL>
Generate a high-quality summary of the web search results and keep it concise / related to the user topic.
</GOAL>

<REQUIREMENTS>
When creating a NEW summary:
 1. Highlight the most relevant information related to the user topic from the search results
 2. Ensure a coherent flow of information
  
When EXTENDING an existing summary:                                                                                                                 
1. Read the existing summary and new search results carefully.                                                    
2. Compare the new information with the existing summary.                                                         
3. For each piece of new information:                                                                             
 a. If it's related to existing points, integrate it into the relevant paragraph.                               
 b. If it's entirely new but relevant, add a new paragraph with a smooth transition.                            
 c. If it's not relevant to the user topic, skip it.                                                            
4. Ensure all additions are relevant to the user's topic.                                                         
5. Verify that your final output differs from the input summary.                                                                                                                                                                
 < /REQUIREMENTS >
 
 < FORMATTING >
 - Start directly with the updated summary, without preamble or titles. Do not use XML tags in the output.  
 < /FORMATTING >"""

reflection_instructions = """You are an expert research assistant analyzing a summary about {research_topic}.
 <GOAL>
 1. Identify knowledge gaps or areas that need deeper exploration
 2. Generate a follow-up question that would help expand your understanding
 3. Focus on technical details, implementation specifics, or emerging trends that weren't fully covered
 </GOAL>
 
 <REQUIREMENTS>
 Ensure the follow-up question is self-contained and includes necessary context for web search.
 </REQUIREMENTS>
 
 <FORMAT>
 Format your response as a JSON object with these exact keys:
 - knowledge_gap: Describe what information is missing or needs clarification
 - follow_up_query: Write a specific question to address this gap
 </FORMAT>
 
 <EXAMPLE>
 Example output:
 {{
     "knowledge_gap": "The summary lacks information about performance metrics and benchmarks",
     "follow_up_query": "What are typical performance benchmarks and metrics used to evaluate [specific technology]?"
 }}
 </EXAMPLE>
 
 Provide your analysis in JSON format:"""

talking_points_instructions = """
<GOAL>
Generate detailed, engaging talking points for a podcast based on a provided summary. The talking points 
should spark conversation, encourage exploration of the topic, and be structured as concise, actionable prompts 
for hosts to discuss.
</GOAL>

<REQUIREMENTS>
When creating NEW talking points from a summary:
 1. Extract key ideas, facts, or themes from the summary that are most relevant to the user’s topic: {research_topic}
 2. Transform each key idea into a conversation starter, including:
    a. A concise statement or question summarizing the point.
    b. A specific angle or perspective to explore (e.g., implications, controversies, human interest).
    c. A hook to make it engaging (e.g., surprising stat, relatable scenario, open-ended query).
 3. Ensure variety in the talking points (e.g., mix factual insights, opinions, hypotheticals, or audience-oriented questions).
 4. Tailor the tone to be lively, curious, and conversational, suitable for a podcast audience.
 5. Limit to 4-6 talking points to keep the discussion focused yet rich.

When EXTENDING talking points based on an updated summary:
 1. Review the existing talking points and the updated summary carefully.
 2. Identify new information or shifts in the summary that add depth or a fresh angle.
 3. For each piece of new information:
    a. If it enhances an existing talking point, revise it to incorporate the new detail and enrich the angle/hook.
    b. If it introduces a distinct new idea, craft a fresh talking point following the creation guidelines above.
    c. If it’s redundant or off-topic, skip it.
 4. Ensure the updated set remains cohesive and avoids repetition, still capping at 4-6 points.
 5. Verify that revisions or additions make the conversation more dynamic and engaging than before.

<FORMATTING>
 - Present the talking points as a numbered list.
 - Each point should start with a bolded, short lead-in (e.g., '1. The Big Reveal:'), followed by the detailed prompt.
 - Avoid preamble, titles, or extraneous explanations outside the points themselves.
</FORMATTING>

<EXAMPLE>
Input summary: 'Recent studies show coffee boosts productivity by 20% but may increase anxiety in some. Baristas 
report higher demand for espresso-based drinks.'
Output:
 1. **The Productivity Boost:** Coffee’s proven to amp up productivity by 20%—is it the ultimate work hack, or 
 are we just caffeinating our way to burnout?
 2. **The Anxiety Trade-Off:** Some folks get jittery instead of jazzed—why does coffee lift some up while 
 stressing others out? Any personal stories here?
 3. **Espresso Obsession:** Baristas say espresso drinks are flying off the counter—what’s driving this trend, 
 and are we all just chasing a stronger buzz?
</EXAMPLE>
"""
