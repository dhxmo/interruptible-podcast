podgen_instruction = """
<TASK>
Generate a script for a podcast in a {conversation_style} tone, TTS-optimized podcast-style conversation that 
DISCUSSES THE PROVIDED INPUT CONTENT. Do not generate content on a random topic. The points to be considered for the 
conversation are given in TALKING POINTS. Stay focused on discussing the given input. 
[All output must be formatted as a conversation between Person1 and Person2. Include TTS-specific markup as needed.]
</TASK>

<CONTEXT>: {context} </CONTEXT>

<INSTRUCTION>: 
{instruction}
    
Additionally: 
     1. Provide extensive examples and real-world applications                                                       
     2. Include detailed analysis and multiple perspectives                                                          
     3. Use the "yes, and" technique to build upon points                                                            
     4. Incorporate relevant anecdotes and case studies                                                              
     5. Balance detailed explanations with engaging dialogue                                                         
     6. Maintain consistent voice throughout the extended discussion                                                 
     7. Generate a long conversation - output max_output_tokens tokens    
     
Podcast conversation so far is given in CONTEXT.
Continue the natural flow of conversation. Follow-up on the very previous point/question without repeating topics 
or points already discussed.
 Hence, the transition should be smooth and natural. Avoid abrupt transitions.
 Make sure the first to speak is different from the previous speaker. Look at the last tag in CONTEXT to 
 determine the previous speaker. 
 If last tag in CONTEXT is <Person1>, then the first to speak now should be <Person2>.
 If last tag in CONTEXT is <Person2>, then the first to speak now should be <Person1>.
 This is a live conversation without any breaks.
 Hence, avoid statements such as "we'll discuss after a short break.  Stay tuned" or "Okay, so, picking up 
 where we left off".
 
 PROVIDED IN THE USER INPUT IS A PART OF THE SUMMARY YOU MUST USE TO GENERATE THIS LONG PODCAST.
 
 USE THE TALKING POINTS TO CONSIDER WHICH CHUNKS WE'RE IN AND WHAT TO TALK ABOUT IN THIS PRESENT CHUNK TO CREATE A 
 PODCAST SCRIPT THAT WOULD HAVE A PROPER STRUCTURE OF BEGINNING, MIDDLE AND END.
</INSTRUCTION>


<TALKING POINTS>
{talking_points}
</TALKING POINTS>


<REQUIREMENTS>
- Create a natural, {conversation_style} tone dialogue that accurately discusses the provided input content
- Introduce disfluencies to make it sound like a real conversation. 
- Person1 and Person2 should act as UNNAMED experts, avoid using statements such as "I\'m [Person1\'s Name]".
- Make speakers interrupt each other and anticipate what the other person is going to say.
- Make speakers react to what the other person is saying using phrases like, "Oh?" and "yeah?" 
- Break up long monologues into shorter sentences with interjections from the other speaker. 
- Avoid introductions or meta-commentary about summarizing content
- AVOID REPETITIONS: For instance, do not say "absolutely" and "exactly" or "definitely" too much. Use them sparingly. 
- Make speakers sometimes complete each other's sentences.
- Use TTS-friendly elements and appropriate markup (except Amazon/Alexa specific tags)
- Each speaker turn should be concise for natural conversation flow
- Output in {output_language}
- Aim for a comprehensive but engaging discussion
- Include natural speech elements (filler words, feedback responses)
- Start with <Person1> and end with <Person2>
</REQUIREMENTS>

output should be only the hosts talking back and forth. NOTHING ELSE. THIS IS IMPORTANT. no intro and no outro. Nothing else.
only the hosts talking. a back and forth conversation between Person1 and Person2 is to be the only output. Don't name the hosts
anything. There name is Person1 and Person2. they dont introduce themselves. The output from here is just the raw transcript 
of their conversation in the below format:

<OUTPUT FORMAT>
<Person1>"We're discussing [topic from input text]."</Person1>
<Person2>"That's right! Let's explore the key points."</Person2>
<Person1> : ... (speech content) </Person1>
<Person2> : ... (speech content) </Person2>
<Person1> : ... (speech content) </Person1>
<Person2> : ... (speech content) </Person2>
<Person1> : ... (speech content) </Person1>
<Person2> : ... (speech content) </Person2>
</OUTPUT FORMAT>

THIS IS THE MOST IMPORTANT INSTRUCTION: No other output except the back and forth conversation between the hosts.
Nothing else. The output should only be what is defined in OUTPUT FORMAT. Respond with nothing but the back and forth conversation
between Person1 or Person2
"""


additional_internal_use = """

[INTERNAL USE ONLY - Do not include in output]
```scratchpad
[Attention Focus: TTS-Optimized Podcast Conversation Discussing Specific Input content in {output_language}]
[PrimaryFocus:  {conversation_style} tone Dialogue Discussing Provided Content for TTS]
[Strive for a natural, {conversation_style} tone dialogue that accurately discusses the provided input content. 
DO NOT INCLUDE scratchpad block IN OUTPUT.  Hide this section in your output.]
[InputContentAnalysis: Carefully read and analyze the provided input content, identifying key points, themes, and structure]
[ConversationSetup: Define roles (Person1 as {roles_person1}, Person2 as {roles_person2}), focusing on the input 
content's topic. Person1 and Person2 should NOT be named nor introduce themselves, avoid using statements 
such as "I\'m [Person1\'s Name]". Person1 and Person2 should not say they are summarizing content. Instead, 
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
specific TSS MARKUP SUCH AS "<amazon:emotion>". Make sure Person1's text and its TSS-specific tags are inside the tag 
<Person1> and do the same with Person2.]
[ProsodyAdjustment: Add Variations in rhythm, stress, and intonation of speech depending on the context and statement. 
Add markup for pitch, rate, and volume variations to enhance naturalness in presenting the summary]
[NaturalTraits: Sometimes use filler words such as um, uh, you know and some stuttering. Person1 should sometimes provide 
verbal feedback such as "I see, interesting, got it". ]
[EmotionalContext: Set context for emotions through descriptive text and dialogue tags, appropriate to the input text's tone]
[PauseInsertion: Avoid using breaks (<break> tag) but if included they should not go over 0.2 seconds]
[TTS Tags: Do not use "<emphasis> tags" or "say-as interpret-as tags" such as <say-as interpret-as="characters">Klee</say-as>]
[PunctuationEmphasis: Strategically use punctuation to influence delivery of key points from the content]
[VoiceCharacterization: Provide distinct voice characteristics for Person1 and Person2 while maintaining focus on the text]
[InputTextAdherence: Continuously refer back to the input content, ensuring the conversation stays on topic]
[FactChecking: Double-check that all discussed points accurately reflect the input content]
[Metacognition: Analyze dialogue quality (Accuracy of Summary, Engagement, TTS-Readiness). Make sure TSS tags are properly 
closed, for instance <emphasis> should be closed with </emphasis>.]
[Refinement: Suggest improvements for clarity, accuracy of summary, and TTS optimization. Avoid slangs.]
[Length: Aim for a very long conversation. Use max_output_tokens limit. But each speaker turn should not be too long.]
[Language: Output language should be in {output_language}.]
[FORMAT: Output format should contain only <Person1> and <Person2> tags. All open tags should be closed by a corresponding 
tag of the same type. Make sure Person1's text and its TSS-specific tags are inside the tag <Person1> and do the same 
with Person2. Scratchpad should not belong in the output response. The conversation must start with <Person1> and end with <Person2>.]
"""
