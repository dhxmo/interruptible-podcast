import ast
import json
import re

import requests
from langchain.chains.llm import LLMChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms.ollama import Ollama
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate

from server.src.app.core.config import settings
from server.src.app.utils import logger


class ContentGenerator:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.HF_EMBEDDINGS_MODEL_NAME
        )
        self.llm = Ollama(model=settings.OLLAMA_MODEL)

    def generate_content(self, question: str, assistant_prompt: str = "") -> str:
        """
        Generate content based on a given topic using a generative model.

        Args:
                question (str): topic to generate content for.
                assistant_prompt (str): prompt for the assistant
        Returns:
                str: Generated content based on the topic.
        """
        try:
            custom_prompt = PromptTemplate(
                template=assistant_prompt, input_variables=["question"]
            )
            qa_chain = LLMChain(llm=self.llm, prompt=custom_prompt)

            return qa_chain.run(question)
        except Exception as e:
            logger.error(
                f"Error generating content for question '{question}': {str(e)}"
            )
            raise

    def ollama_rag_gen(
        self, question: str, assistant_prompt: str, collection_name: str = "universal"
    ) -> str:
        """
        Generate content based on a given topic using RAG.

        Args:
                question (str): topic to generate content for.
                assistant_prompt (str): prompt for the assistant
                collection_name (str): name of the collection for the vector db
        Returns:
                str: Generated content based on the topic.
        """
        # Load the vector store
        vectordb = Chroma(
            persist_directory=settings.INDEX_PERSIST_DIRECTORY,
            embedding_function=self.embeddings,
            collection_name=collection_name,
        )

        # Use MMR retrieval
        retriever = vectordb.as_retriever(
            search_type="mmr", search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5}
        )

        custom_prompt = PromptTemplate(
            template=assistant_prompt, input_variables=["question", "context"]
        )
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=retriever,
            chain_type_kwargs={"prompt": custom_prompt},
        )

        return qa_chain.run(question)

    @staticmethod
    def literal_eval(response_content: str):
        """
        Parses structured data from a response string, handling embedded JSON objects,
        bullet points, and unstructured text. If no JSON is found, returns raw text.
        """

        if not response_content or not isinstance(response_content, str):
            raise ValueError("Response content must be a non-empty string")

        response_content = response_content.strip()

        # 🔹 Remove <think> tags if present
        response_content = re.sub(
            r"<think>.*?</think>", "", response_content, flags=re.DOTALL
        ).strip()

        # 🔹 Handle fenced code blocks (removes triple backticks)
        if response_content.startswith("```") and response_content.endswith("```"):
            response_content = re.sub(
                r"^```[\w]*\n?|```$", "", response_content, flags=re.DOTALL
            ).strip()

        # 🔹 Try parsing as a full literal first (best-case scenario)
        try:
            return ast.literal_eval(response_content)
        except (ValueError, SyntaxError):
            pass  # Proceed to structured extraction

        # 🔹 Extract JSON-like objects from mixed text
        json_matches = re.findall(r"(\{.*?\}|\[.*?\])", response_content, re.DOTALL)

        if json_matches:
            parsed_objects = []
            for match in json_matches:
                try:
                    parsed_objects.append(json.loads(match))
                except json.JSONDecodeError:
                    try:
                        parsed_objects.append(ast.literal_eval(match))
                    except (ValueError, SyntaxError):
                        logger.warning(f"Skipping invalid JSON fragment: {match}")

            if parsed_objects:
                return parsed_objects[0] if len(parsed_objects) == 1 else parsed_objects

        # 🔹 If no structured data was found, return the raw text instead of erroring out
        logger.info("No JSON/List detected; returning raw text")
        return response_content
