import logging
import re
from typing import Dict, Any

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from src.config import Config
from src.pod_gen.clean import ContentCleanerMixin
from src.pod_gen.pg_templates import (
    interruption_system_instruction,
    interruption_user_instruction,
)
from src.pod_gen.pg_templates import podgen_instruction, user_instruction


class PodGenStandard:
    def __init__(self):
        self.llm = ChatOllama(
            base_url=Config.ollama_base_url,
            model=Config.local_llm_podcast_gen,
            temperature=0.3,
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name=Config.HF_EMBEDDINGS_MODEL_NAME
        )

    async def podgen(
        self,
        session: Dict[str, Any],
        talking_points: str,
    ):
        result = await self.llm.ainvoke(
            [
                SystemMessage(
                    content=podgen_instruction.format(
                        running_summary=session["running_summary"],
                    )
                ),
                HumanMessage(
                    content=user_instruction.format(
                        talking_points=talking_points,
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

        return clean_script

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

    async def interruption_gen(
        self,
        user_query: str,
        session: Dict[str, Any],
    ) -> str:
        """tried RAG didn't work too well. ideally that's what should be used"""

        logging.info("handling interruption gen")

        result = await self.llm.ainvoke(
            [
                SystemMessage(content=interruption_system_instruction),
                HumanMessage(
                    content=interruption_user_instruction.format(
                        question=user_query,
                        running_summary=session["running_summary"],
                    )
                ),
            ]
        )

        return result.content
