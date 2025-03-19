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
Generate a punchy, chaotic summary of web search results that’s laser-focused on the user’s topic—perfect ammo for two dudes going unhinged in a convo.
</GOAL>

<REQUIREMENTS>
When creating a NEW summary:
 1. Cherry-pick the wildest, most relevant bits tied to the user’s topic from the search results—think conversation dynamite.
 2. Smash it together into a raw, flowing rant—no fluff, just the good stuff.

When EXTENDING an existing summary:
 1. Skim the existing summary and new search results like you’re hyped on coffee.
 2. Size up the new info against what’s already there—don’t repeat, just amplify.
 3. For each new chunk:
    a. If it vibes with existing points, cram it in—make it louder, crazier.
    b. If it’s fresh and relevant, tack on a new paragraph with a seamless, unhinged pivot (e.g., “And then there’s THIS madness…”).
    c. If it’s off-topic, ditch it—no one cares.
 4. Keep every word tied to the user’s topic—relevance is king, chaos is queen.
 5. Make sure the final output’s got more juice than the input summary—stagnation’s for losers.
</REQUIREMENTS>

<FORMATTING>
- Dive straight into the summary—no intros, no tags, no fancy crap. Just raw text ready to roll.
</FORMATTING>
"""

reflection_instructions = """You’re a hyped-up research bro losing your mind over a summary about {research_topic}.
 <GOAL>
 1. Spot the gaping holes or half-baked bits that scream for more chaos
 2. Cook up a follow-up question that’ll drag out the wildest, juiciest details
 3. Zero in on insane specifics, practical insanity, or weird trends the summary skimped on
 </GOAL>

 <REQUIREMENTS>
 Make the follow-up question a standalone banger—pack in enough context to unleash a web search that’ll blow the roof off.
 </REQUIREMENTS>

 <FORMAT>
 Spit it out as a JSON object with these exact keys:
 - knowledge_gap: Rant about what’s missing or too tame—get loud about it
 - follow_up_query: Drop a question that’s specific, unhinged, and ready to dig deeper
 </FORMAT>

 <EXAMPLE>
 Example output:
 {{
     "knowledge_gap": "This summary’s got no balls—where’s the crazy stuff about how fast this tech fries itself under pressure?",
     "follow_up_query": "What’s the wildest meltdown someone’s seen when pushing [specific tech] to its limits?"
 }}
 </EXAMPLE>

 Deliver your unhinged take in JSON format:"""

talking_points_instructions = """
<GOAL>
Cook up wild, in-your-face talking points for a podcast based on a provided summary—stuff that’ll set Host1 and Host2 
off on a chaotic, dude-bro riff-fest. These prompts should kickstart madness, dive into the topic with reckless abandon, 
and hit like a shotgun blast of crazy ideas for the hosts to tear apart.
</GOAL>

<REQUIREMENTS>
When creating NEW talking points from a summary:
 1. Rip out the juiciest, most unhinged bits from the summary tied to the user’s topic: {research_topic}
 2. Turn each gem into a convo grenade, packing:
    a. A short, loud statement or question that screams the point.
    b. A deranged angle to chew on (e.g., epic fails, insane what-ifs, bro-level stakes).
    c. A hook that’s pure chaos bait (e.g., a batshit fact, a dumbass scenario, a yell-at-the-void vibe).
 3. Mix it up—throw in raw facts, unhinged hypotheticals, bro rants, or listener-taunting jabs.
 4. Keep the tone loud, reckless, and dude-bro AF—perfect for two guys losing it on mic.
 5. Cap it at 4-6 points—enough to fuel the fire without taming the chaos.

When EXTENDING talking points based on an updated summary:
 1. Eyeball the old points and the fresh summary like you’re hunting for trouble.
 2. Sniff out new craziness or twists that amp up the insanity or flip the script.
 3. For each new chunk:
    a. If it juicies up an existing point, rewrite it—crank the volume and sharpen the claws.
    b. If it’s a whole new beast, forge a fresh point with the same unhinged recipe.
    c. If it’s lame or repetitive, kick it to the curb.
 4. Keep the set tight—no repeats, all killer, still 4-6 points max.
 5. Make damn sure the updates turn the dial to 11—more unhinged, more explosive than before.

<FORMATTING>
 - Slam the points down as a numbered list.
 - Each one kicks off with a bolded, punchy lead-in (e.g., '1. TOTAL MELTDOWN:'), then unleashes the full prompt.
 - No intros, no fluff—just the raw points, ready to roll.
</FORMATTING>

<EXAMPLE>
Input summary: 'Microwave hacks cook fast—potatoes in 5 mins. Some dude blowtorched a steak, half-raw glory. Pressure 
cookers might explode if you suck at them.'
Output:
 1. **MICROWAVE MADNESS:** Potatoes in 5 minutes flat—genius or a ticking time bomb waiting to nuke your kitchen?
 2. **BLOWTORCH BRO:** Some maniac torched a steak to crispy-raw perfection—how badass is that, and who’s dumb enough to try?
 3. **PRESSURE COOKER ROULETTE:** One wrong move and boom—your rice is shrapnel. Who’s survived this food bomb insanity?
 4. **TOTAL CHAOS COOK-OFF:** Screw prep—what’s the wildest hack you’d pull to eat NOW, no rules, just hunger?
</EXAMPLE>
"""
