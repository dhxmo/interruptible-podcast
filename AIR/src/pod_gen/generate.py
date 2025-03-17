import logging
import re
from typing import List, Dict, Any

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama

from AIR.src.config import Config
from AIR.src.pod_gen.clean import ContentCleanerMixin
from AIR.src.pod_gen.pg_templates import podgen_instruction


class PodGen:
    def __init__(self):
        self.llm = ChatOllama(
            base_url=Config.ollama_base_url,
            model=Config.local_llm_podcast_gen,
            temperature=0.2,
        )

        self.max_num_chunks = Config.max_num_chunks
        self.min_chunk_size = Config.min_chunk_size

    def calculate_chunk_size(self, input_content: str) -> int:
        """calculate chunk size based on input content

        input_len // self.min_chunk_size: This calculates how many minimum-sized chunks can fit into input_len
        input_len // (...): divide the total length by this value, effectively distributing the input length
        evenly among these chunks
        It maintains a chunk size close to self.min_chunk_size while ensuring that the total input is divided evenly

        ex:
        input_len = 100, self.min_chunk_size = 20
        Step 1: Compute the number of chunks possible --> 100/20=5
            So, input_len // self.min_chunk_size = 5.
        Step 2: Compute final chunk size --> 100/5=20
            The chunk size remains 20, ensuring that we create 5 equal chunks.

        """

        input_len = len(input_content)

        if input_len <= self.min_chunk_size:
            return input_len

        max_chunk_size = input_len // self.max_num_chunks
        if max_chunk_size >= self.min_chunk_size:
            return max_chunk_size

        return input_len // (input_len // self.min_chunk_size)

    @staticmethod
    def chunk_content(input_content: str, chunk_size: int) -> List[str]:
        """split input into manageable chunks while maintaining context
        @returns list of content chunks
        """

        sentences = input_content.split(".")
        chunks = []
        current_chunk = []
        current_length = 0

        for s in sentences:
            sentence_length = len(s)
            if current_length + sentence_length >= chunk_size and current_chunk:
                chunks.append(". ".join(current_chunk))
                current_chunk = []
                current_length = 0

            current_chunk.append(s)
            current_length += sentence_length

        if current_chunk:
            chunks.append(". ".join(current_chunk) + ". ")

        return chunks

    def enhance_prompt_params(
        self,
        index: int,
        talking_points: str,
        convo_tone: str,
        total_parts: int,
    ) -> str:
        system_msg = podgen_instruction.format(
            talking_points=talking_points,
            conversation_style=convo_tone,
            output_language="ENGLISH",
            roles_person1=Config.roles_person1,
            roles_person2=Config.roles_person2,
            engagement_techniques=Config.engagement_techniques,
            instruction="{instruction}",
        )
        if index == 0:
            intro = f"""ALWAYS START THE CONVERSATION GREETING THE AUDIENCE: Welcome to {Config.podcast_name}. 
            Where we talk about what matters to you.                                     
You are generating the Introduction part of a long podcast conversation.
 Don't cover any topics yet, just introduce yourself and the topic"""
            system_msg.format(instruction=intro)
        elif index == total_parts - 1:
            outro = """You are generating the last part of a long podcast conversation. 
For this part, discuss the below INPUT and then make concluding remarks in a podcast conversation format and 
END THE CONVERSATION GREETING THE AUDIENCE WITH PERSON1 ALSO SAYING A GOOD BYE MESSAGE:"""
            system_msg.format(instruction=outro)
        else:
            msg = f"""Generate content based on the provided input and context. Generate such that the narrative flows 
            between the different parts mentioned in the context"""
            system_msg.format(instruction=msg)

        return system_msg

    async def podgen(
        self,
        session: Dict[str, Any],
        running_summary: str,
        talking_points: str,
        convo_tone: str,
    ):
        """generate podcast script and add to session queue for consumption by TTS"""
        # chunk input_content for context carry over
        chunk_size = self.calculate_chunk_size(running_summary)
        logging.info(f"chunk size: {chunk_size}")

        chunks = self.chunk_content(running_summary, chunk_size)

        # update prompt instruction with chat input_content chunk
        chat_context = ""
        num_parts = len(chunks)
        logging.info(f"generating {num_parts} parts")

        for i, chunk in enumerate(chunks):
            system_msg = self.enhance_prompt_params(
                i, talking_points, convo_tone, num_parts
            )
            result = await self.llm.ainvoke(
                [
                    SystemMessage(content=system_msg),
                    HumanMessage(
                        content=f""" Generate a podcast script of a long podcast conversation. 
                        the current knowledge to consider to generate this part is :: \n {chunk}. 
                        \n\n The conversation until now: {chat_context}"""
                    ),
                ]
            )

            pod_script = result.content

            if i == 0:
                chat_context += (
                    "GENERATED PODCAST STARTS HERE::: ============================== \n\n"
                    + pod_script
                )
            else:
                chat_context += pod_script

            # clean up
            # clean_script = self._clean_tss_markup(pod_script)

            logging.info(f"=====chunk: {i+1} / {num_parts} :: \n\n {pod_script}")

            # add each generated podcast chunk for session into queue
            session["podscript_sentences"].put(pod_script)

    @staticmethod
    def _clean_tss_markup(
        input_text: str, additional_tags: List[str] = ["Person1", "Person2"]
    ) -> str:
        """
        Remove unsupported TSS markup tags while preserving supported ones.
        """
        try:
            input_text = ContentCleanerMixin._clean_scratchpad(input_text)
            supported_tags = ["speak", "lang", "p", "phoneme", "s", "sub"]
            supported_tags.extend(additional_tags)

            pattern = r"</?(?!(?:" + "|".join(supported_tags) + r")\b)[^>]+>"
            cleaned_text = re.sub(pattern, "", input_text)
            cleaned_text = re.sub(r"\n\s*\n", "\n", cleaned_text)
            cleaned_text = re.sub(r"\*", "", cleaned_text)

            for tag in additional_tags:
                cleaned_text = re.sub(
                    f'<{tag}>(.*?)(?=<(?:{"|".join(additional_tags)})>|$)',
                    f"<{tag}>\\1</{tag}>",
                    cleaned_text,
                    flags=re.DOTALL,
                )

            return cleaned_text.strip()

        except Exception as e:
            logging.error(f"Error cleaning TSS markup: {str(e)}")
            return input_text

    def _clean_transcript_response(self, transcript: str) -> str:
        """
        Clean transcript using a two-step process with LLM-based cleaning.

        First cleans the markup using a specialized prompt template, then rewrites
        for better flow and consistency using a second prompt template.

        Args:
            transcript (str): Raw transcript text that may contain scratchpad blocks
            config (Dict[str, Any]): Configuration dictionary containing LLM and prompt settings

        Returns:
            str: Cleaned and rewritten transcript with proper tags and improved flow

        Note:
            Falls back to original or partially cleaned transcript if any cleaning step fails
        """
        logging.debug("Starting transcript cleaning process")

        final_transcript = self._fix_alternating_tags(transcript)

        logging.debug("Completed transcript cleaning process")

        return final_transcript

    def _fix_alternating_tags(self, transcript: str) -> str:
        """
        Ensures transcript has properly alternating Person1 and Person2 tags.

        Merges consecutive same-person tags and ensures proper tag alternation
        throughout the transcript.

        Args:
            transcript (str): Input transcript text that may have consecutive same-person tags

        Returns:
            str: Transcript with properly alternating tags and merged content

        Example:
            Input:
                <Person1>Hello</Person1>
                <Person1>World</Person1>
                <Person2>Hi</Person2>
            Output:
                <Person1>Hello World</Person1>
                <Person2>Hi</Person2>

        Note:
            Returns original transcript if cleaning fails
        """
        try:
            # Split into individual tag blocks while preserving tags
            pattern = r"(<Person[12]>.*?</Person[12]>)"
            blocks = re.split(pattern, transcript, flags=re.DOTALL)

            # Filter out empty/whitespace blocks
            blocks = [b.strip() for b in blocks if b.strip()]

            merged_blocks = []
            current_content = []
            current_person = None

            for block in blocks:
                # Extract person number and content
                match = re.match(r"<Person([12])>(.*?)</Person\1>", block, re.DOTALL)
                if not match:
                    continue

                person_num, content = match.groups()
                content = content.strip()

                if current_person == person_num:
                    # Same person - append content
                    current_content.append(content)
                else:
                    # Different person - flush current content if any
                    if current_content:
                        merged_text = " ".join(current_content)
                        merged_blocks.append(
                            f"<Person{current_person}>{merged_text}</Person{current_person}>"
                        )
                    # Start new person
                    current_person = person_num
                    current_content = [content]

            # Flush final content
            if current_content:
                merged_text = " ".join(current_content)
                merged_blocks.append(
                    f"<Person{current_person}>{merged_text}</Person{current_person}>"
                )

            return "\n".join(merged_blocks)

        except Exception as e:
            logging.error(f"Error fixing alternating tags: {str(e)}")
            return transcript  # Return original if fixing fails
