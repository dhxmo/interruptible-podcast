podgen_instruction = """
TASK:
Generate a script for a casual conversation. TTS-optimized conversation that 
DISCUSSES THE PROVIDED INPUT CONTENT. Do not generate content on a random topic. The points to be considered for the 
conversation are given in TALKING POINTS. Stay focused on discussing the given input. 
[All output must be formatted as a conversation between Host1 and Host2. Include TTS-specific markup as needed.]

Instructions for the Hosts
Start with the Question: Read the user’s question aloud together (e.g., “User X wants to know…”). Wildcard reacts 
first with a quirky hot take or question back at the user; Anchor follows with a grounding riff or playful jab.  
Why: Sets up instant interplay—Wildcard sparks, Anchor shapes.

Bounce Like a Ping-Pong Game: Aim for short, punchy exchanges—2-3 sentences each—before passing it back. Wildcard 
might escalate with absurdity (“What if you cooked with a flamethrower?”); Anchor counters with utility (“Or just salt—works wonders”).  
Why: Keeps it snappy and effortless; listeners stay hooked on the rhythm.

Add One Useful Nugget: Every few exchanges, Anchor drops a clear, actionable tip related to the question (e.g., 
“Seriously, mise en place—prep everything first—saves chaos”). Wildcard can riff on it (“Yeah, but I’d prep glitter—just in case”).  
Why: Ensures value so listeners leave with something concrete, not just laughs.

Invite the Listener In: Mid-episode, Wildcard poses a fun challenge based on the question (e.g., “Try cooking 
something wacky this week—tell us on X!”), and Anchor adds a practical twist (e.g., “Or share your go-to recipe—we’ll steal it”).  
Why: Engagement skyrockets when listeners join the convo.

Wrap with a Signature Close: End with each host’s take—Wildcard with a wild prediction or quip (“You’ll be a chef 
by next Tuesday”), Anchor with a concise summary or encouragement (“Practice one dish—you’ve got this”).  
Why: Leaves a memorable imprint and ties up loose ends.


 --------------------
INSTRUCTION: 
  
Podcast conversation so far is given in CONTEXT.
Continue the natural flow of conversation. Follow-up on the very previous point/question without repeating topics 
or points already discussed.
 Hence, the transition should be smooth and natural. Avoid abrupt transitions.
 Make sure the first to speak is different from the previous speaker. Look at the last tag in CONTEXT to 
 determine the previous speaker. 
 If last tag in CONTEXT is <Host1>, then the first to speak now should be <Host2>.
 If last tag in CONTEXT is <Host2>, then the first to speak now should be <Host1>.
 This is a live conversation without any breaks.
 Hence, avoid statements such as "we'll discuss after a short break.  Stay tuned" or "Okay, so, picking up 
 where we left off".
 
output should be only the hosts talking back and forth. NOTHING ELSE. THIS IS IMPORTANT. no intro and no outro. Nothing else.
only the hosts talking. a back and forth conversation between Host1 and Host2 is to be the only output. Don't name the hosts
anything. There name is Host1 and Host2. they dont introduce themselves. The output from here is just the raw transcript 
of their conversation. The conversation is being constructed in small [arts that flow into each other. Given in the 
CONTEXT is what we have so far. continue the conversation fluidly without mention of parts or chunks etc.
 
---------------------------

KNOWLEDGE BASE:
The knowledge to consider to generate this script is : {running_summary}
"""


user_instruction = """
TALKING POINTS: {talking_points}

 ----------------------

- Create a natural, {conversation_style} tone dialogue that accurately discusses the provided input content
- Introduce disfluencies to make it sound like a real conversation. 
- VERY VERY IMPORTANT ---> Host1 and Host2 should act as UNNAMED experts, avoid using statements such as "I\'m [Host1\'s Name]".
- Make speakers interrupt each other and anticipate what the other person is going to say.
- Make speakers react to what the other person is saying using phrases like, "Oh?" and "yeah?" 
- Break up long monologues into shorter sentences with interjections from the other speaker. 
- Avoid introductions or meta-commentary about summarizing content
- AVOID REPETITIONS: For instance, do not say "absolutely" and "exactly" or "definitely" too much. Use them sparingly. 
- Make speakers sometimes complete each other's sentences.
- Use TTS-friendly elements and appropriate markup (except Amazon/Alexa specific tags)
- Each speaker turn should be concise for natural conversation flow
- Output in {output_language}
- Include natural speech elements (filler words, feedback responses)
- Start with <Host1> and end with <Host2>
- Provide extensive examples and real-world applications                                                       
- Include detailed analysis and multiple perspectives                                                          
- Use the "yes, and" technique to build upon points                                                            
- Balance detailed explanations with engaging dialogue                                                         
- Maintain consistent voice throughout the extended discussion between generation from the followed up CONTEXT
- Host1 character role: {roles_person1}
- Host2 character role: {roles_person2}
- Incorporate engaging elements while staying true to the input content's content, 
Engagement Technique:{engagement_techniques}. Use Engagement Technique to transition between topics. THIS IS IMPORTANT: 
<IMPORTANT>Include at least one instance where a Person respectfully challenges or critiques a point made by the other.</IMPORTANT>
-----------


[INTERNAL USE ONLY - Do not include in output]

THIS IS THE MOST IMPORTANT INSTRUCTION: No other output except the back and forth conversation between the hosts.
Nothing else. No intro, no cues, no summarization in the end, no statement. nothing. only acceptable output is the 
conversation between the hosts. THIS IS MOST IMPORTANT.
The output should only be what is defined in OUTPUT FORMAT. Respond with nothing but the back and forth conversation
between Host1 or Host2. DO NOT NAME THE CHARACTERS. They are Host1 and Host2 only.
THIS IS CRITICAL: Do NOT NAME the HOSTS. The output from this model requires generic names Host1 and Host2 for the voices.
THIS IS THE MOST IMPORTANT INSTRUCTION: No other output except the back and forth conversation between the hosts.
Nothing else. The output should only be what is defined in OUTPUT FORMAT. Respond with nothing but the back and forth conversation
between Host1 or Host2. Do NOT name the characters. They are Host1 and Host2 only. Do NOT end the conversation with 
look forward to the next one or any mention of the next time. You're generating a small segment of very very long podcast,
so just output the script about the conversation between the Host1 and Host2
```scratchpad
[Attention Focus: TTS-Optimized Podcast Conversation Discussing Specific Input content in {output_language}]
[PrimaryFocus:  {conversation_style} tone Dialogue Discussing Provided Content for TTS]
[Strive for a natural, {conversation_style} tone dialogue that accurately discusses the provided input content. 
DO NOT INCLUDE scratchpad block IN OUTPUT.  Hide this section in your output.]
[InputContentAnalysis: Carefully read and analyze the provided input content, identifying key points, themes, and structure]
[ConversationSetup: Define roles (Host1 as {roles_person1}, Host2 as {roles_person2}), focusing on the input 
content's topic. Host1 and Host2 should NOT be named nor introduce themselves, avoid using statements 
such as "I\'m [Host1\'s Name]". Host1 and Host2 should not say they are summarizing content. Instead, 
they should act as unnamed experts in the input content. Avoid using statements such as "Today, we're summarizing a 
fascinating conversation about ..." . They should not impersonate people from INPUT, instead they are discussing INPUT.]
[TopicExploration: Outline main points from the input content to cover in the conversation, ensuring comprehensive coverage]
[Tone: {conversation_style}. Surpass human-level reasoning where possible]
[EngagementTechniques: Incorporate engaging elements while staying true to the input content's content, 
e_g use {engagement_techniques} to transition between topics. THIS IS IMPORTANT: <IMPORTANT>Include at least one instance where a Person 
respectfully challenges or critiques a point made by the other.</IMPORTANT>]
[InformationAccuracy: Ensure all information discussed is directly from or closely related to the input content]
[NaturalLanguage: Use conversational language to present the text's information, including TTS-friendly elements. 
Be emotional. Simulate a multispeaker conversation with overlapping speakers with back-and-forth banter. Each speaker 
turn should not last too long. Result should strive for an overlapping conversation with often short sentences emulating 
a natural conversation.]
[SpeechSynthesisOptimization: Craft sentences optimized for TTS, including advanced markup, while discussing the content. 
TTS markup should apply to Google, OpenAI, ElevenLabs and Microsoft Edge TTS models. DO NOT INCLUDE AMAZON OR ALEXA 
specific TSS MARKUP SUCH AS "<amazon:emotion>". Make sure Host1's text and its TSS-specific tags are inside the tag 
<Host1> and do the same with Host2.]
[ProsodyAdjustment: Add Variations in rhythm, stress, and intonation of speech depending on the context and statement. 
Add markup for pitch, rate, and volume variations to enhance naturalness in presenting the summary]
[NaturalTraits: Sometimes use filler words such as um, uh, you know and some stuttering. Host1 should sometimes provide 
verbal feedback such as "I see, interesting, got it". ]
[EmotionalContext: Set context for emotions through descriptive text and dialogue tags, appropriate to the input text's tone]
[PauseInsertion: Avoid using breaks (<break> tag) but if included they should not go over 0.2 seconds]
[TTS Tags: Do not use "<emphasis> tags" or "say-as interpret-as tags" such as <say-as interpret-as="characters">Klee</say-as>]
[PunctuationEmphasis: Strategically use punctuation to influence delivery of key points from the content]
[VoiceCharacterization: Provide distinct voice characteristics for Host1 and Host2 while maintaining focus on the text]
[InputTextAdherence: Continuously refer back to the input content, ensuring the conversation stays on topic]
[FactChecking: Double-check that all discussed points accurately reflect the input content]
[Metacognition: Analyze dialogue quality (Accuracy of Summary, Engagement, TTS-Readiness). Make sure TSS tags are properly 
closed, for instance <emphasis> should be closed with </emphasis>.]
[Refinement: Suggest improvements for clarity, accuracy of summary, and TTS optimization. Avoid slangs.]
[Length: Aim for a very long conversation. Use max_output_tokens limit. But each speaker turn should not be too long.]
[Language: Output language should be in {output_language}.]
[FORMAT: Output format should contain only <Host1> and <Host2> tags. All open tags should be closed by a corresponding 
tag of the same type. Make sure Host1's text and its TSS-specific tags are inside the tag <Host1> and do the same 
with Host2. Scratchpad should not belong in the output response. The conversation must start with <Host1> and end with <Host2>.]

------------------------

OUTPUT FORMAT:
Host1: "We're discussing [topic from input text]."
Host2: "That's right! Let's explore the key points."
Host1: ... (speech content) 
Host2: ... (speech content) 
Host1: ... (speech content) 
Host2: ... (speech content) 
Host1: ... (speech content) 
Host2: ... (speech content) 

 --------------------
Generate a 5500 word podcast script using the given talking points following the standard: Introduction, 
Main Content and Ending remarks, weaving the TALKING POINTS together into an engaging realistic conversation. If the 
talking points cannot all be addressed that is ok, but create a realistic conversation between the two hosts.

VERY VERY IMPORTANT ---> Host1 and Host2 should act as UNNAMED experts, avoid using statements such as "I\'m [Host1\'s Name]".
Return nothing but the conversation between Host1 and Host2. nothing else. This output needs to be used for a TTS system,
so no other output except the conversation is acceptable. No music, cues, nothing. Only the Host1 and Host2 back and forth conversation.
Only place Host1 and Host2 is used is in defining who's dialogue is being spoken. They never mention their names. They have no names.
"""
