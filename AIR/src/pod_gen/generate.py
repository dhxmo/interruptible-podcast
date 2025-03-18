import logging
import re
from typing import Dict, Any

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama

from src.config import Config
from src.pod_gen.clean import ContentCleanerMixin
from src.pod_gen.pg_templates import podgen_instruction, user_instruction


class PodGenStandard:
    def __init__(self):
        self.llm = ChatOllama(
            base_url=Config.ollama_base_url,
            model=Config.local_llm_reasoning,
            temperature=0.2,
        )

    async def podgen(
        self,
        session: Dict[str, Any],
        running_summary: str,
        talking_points: str,
        convo_tone: str,
    ):
        result = await self.llm.ainvoke(
            [
                SystemMessage(
                    content=podgen_instruction.format(
                        running_summary=running_summary,
                        conversation_style=convo_tone,
                        output_language="ENGLISH",
                        roles_person1=Config.roles_person1,
                        roles_person2=Config.roles_person2,
                        engagement_techniques=Config.engagement_techniques,
                    )
                ),
                HumanMessage(
                    content=user_instruction.format(
                        talking_points=talking_points,
                        conversation_style=convo_tone,
                        output_language="ENGLISH",
                        roles_person1=Config.roles_person1,
                        roles_person2=Config.roles_person2,
                        engagement_techniques=Config.engagement_techniques,
                    )
                ),
            ]
        )

        pod_script = result.content

        # needed for deepseek reasoning models :
        # Remove everything inside <think>...</think> including the tags
        clean_script = re.sub(
            r"<think>.*?</think>\n?", "", pod_script, flags=re.DOTALL
        ).strip()

        logging.info(f"=====clean script:: \n\n {clean_script}")

        session["podscript_script"] = clean_script

    @staticmethod
    def _clean_tss_markup(input_text: str, additional_tags=None) -> str:
        """
        Remove unsupported TSS markup tags while preserving supported ones.
        """
        if additional_tags is None:
            additional_tags = ["Host1", "Host2"]
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
