import asyncio
import json
import logging
import re
from typing import List, Dict, Any, Iterable

import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .dr_templates import (
    query_writer_instructions,
    summarizer_instructions,
    reflection_instructions,
    talking_points_instructions,
    content_extraction_instructions,
)
from .util import deduplicate_and_format_sources
from ..config import Config


class DeepResearcher:
    def __init__(self):
        self.llm = ChatOllama(
            base_url=Config.ollama_base_url,
            model=Config.local_llm,
            temperature=0.2,
        )

        # talking points and reflect with reasoning model; rest with the standard model
        self.llm_reasoning = ChatOllama(
            base_url=Config.ollama_base_url,
            model=Config.local_llm_reasoning,
            temperature=0.2,
        )

        self.llm_json_mode = ChatOllama(
            base_url=Config.ollama_base_url,
            model=Config.local_llm,
            temperature=0.2,
            format="json",
        )

        self.llm_reasoning_json_mode = ChatOllama(
            base_url=Config.ollama_base_url,
            model=Config.local_llm_reasoning,
            temperature=0.2,
            format="json",
        )

    async def generate_report(
        self,
        user_input: str,
        session: dict[str, Any],
    ) -> str | None:
        """
        Entrypoint function to conduct research on topic and generate talking points for conversation

        :param user_input:
        :param session:
        :return:
        """
        # generate query
        query = await self.generate_query(user_input)
        session["research_topic"] = query
        session["follow_up_query"] = query

        count = Config.research_loop_count

        while count > 0:
            # concurrent i/o bound task
            search_result = await self.web_search_n_scrape(
                session, session["follow_up_query"]
            )
            logging.info("search done")
            session["web_search_results"].append(search_result)

            current_summary = await self.summarize_sources(session)
            logging.info("summary generated")

            # append new summarized knowledge to the previous knowledge
            session["running_summary"] += current_summary

            count -= 1

            # if not last research loop continue
            if count == 0:
                logging.info("last loop, generating talking points")
                break

            session["follow_up_query"] = await self.reflect(session)
            logging.info("summary reflected")

        talking_points = await self.generate_talking_points(session)

        logging.info(f"\n\ntalking points generated::: {talking_points}")
        logging.info(f"\n\nrunning summary generated::: {session['running_summary']}")

        return talking_points

    async def generate_query(self, user_input: str) -> str | None:
        try:
            query_writer_instructions_formatted = query_writer_instructions.format(
                research_topic=user_input
            )

            result = await self.llm_json_mode.ainvoke(
                [
                    SystemMessage(content=query_writer_instructions_formatted),
                    HumanMessage(content="Generate a query for web search:"),
                ]
            )
            query = json.loads(result.content)

            return query["query"]
        except Exception as e:
            logging.error("error in generate query", str(e))

    async def web_search_n_scrape(
        self, session: dict[str, Any], search_query: str
    ) -> str | None:
        """gather search results and scrape content for later use"""
        logging.info("init web search")
        try:
            # --- get search results
            search_results = await self.duckduckgosearch(
                search_query,
                max_results=Config.search_max_results,
            )
            logging.info("search_results done")

            # --- scrape and embed content for reuse later for questioning
            # Create a list of coroutines while maintaining index association
            tasks = [
                self.embed_url(session, result["url"], session_id=Config.uuid)
                for result in search_results
            ]

            # Run all coroutines concurrently
            mds_results = await asyncio.gather(*tasks)

            # Attach the embeddings back to the respective search results
            for index, embedding in enumerate(mds_results):
                search_results[index][
                    "raw_content"
                ] = embedding  # Assign embedding to corresponding search result

            return deduplicate_and_format_sources(
                search_response=search_results,
                max_tokens_per_response=Config.max_tokens_per_resource,
                include_raw_content=True,
            )

        except Exception as e:
            logging.error("error in web search", str(e))

    async def summarize_sources(self, session: dict[str, Any]) -> str | None:
        """summarize search results"""
        logging.info("init summarize sources")
        try:
            existing_summary = session.get("running_summary")
            most_recent_web_search = session.get("web_search_results")[-1]

            # build human msg
            if existing_summary:
                human_msg_content = (
                    f"<User Input> \n {session.get('research_topic')} \n <User Input>\n\n"
                    f"<Existing Summary> \n {existing_summary} \n <Existing Summary>\n\n"
                    f"<New Search Results> \n {most_recent_web_search} \n <New Search Results>"
                )
            else:
                human_msg_content = (
                    f"<User Input> \n {session.get('research_topic')} \n <User Input>\n\n"
                    f"<Search Results> \n {most_recent_web_search} \n <New Search Results>"
                )

            result = await self.llm.ainvoke(
                [
                    SystemMessage(content=summarizer_instructions),
                    HumanMessage(content=human_msg_content),
                ]
            )
            running_summary = result.content

            # deepseek specific
            if (
                "deepseek" in Config.local_llm
                or "deepseek" in Config.local_llm_reasoning
            ):
                while "<think>" in running_summary and "</think" in running_summary:
                    # remove think section from the final output
                    start = running_summary.find("<think>")
                    end = running_summary.find("</think>") + len("</think>")
                    running_summary = running_summary[:start] + running_summary[end:]

            return running_summary

        except Exception as e:
            logging.error("error in summarize sources", str(e))

    async def reflect(self, session: dict[str, Any]) -> str | None:
        try:
            result = await self.llm_reasoning_json_mode.ainvoke(
                [
                    SystemMessage(
                        content=reflection_instructions.format(
                            research_topic=session.get("research_topic")
                        )
                    ),
                    HumanMessage(
                        content=f"Identify a knowledge gap and generate a follow-up web search query based on our existing knowledge: {session.get('running_summary')}"
                    ),
                ]
            )
            follow_up_query = json.loads(result.content)

            query = follow_up_query.get("follow_up_query")

            if not query:
                return f"Tell me about {session.get('research_topic')}"

            return query

        except Exception as e:
            logging.error("error in reflect", str(e))

    @staticmethod
    async def duckduckgosearch(query: str, max_results: int) -> List[Dict[str, str]]:
        """
        @returns
        list: all search responses
        - results[list] - list of all search maps
            - title (str)
            - url (str)
            - content (str) - summary
        """

        try:
            # get search results
            with DDGS() as ddgs:
                results = []

                search_results = ddgs.text(query, max_results=max_results)

                for r in search_results:
                    url = r.get("href")
                    title = r.get("title")
                    body = r.get("body")

                    if not all([url, title, body]):
                        logging.error("incomplete results from ddg", r)
                        continue

                    # add to results
                    result = {
                        "title": title,
                        "url": url,
                        "content": body,
                    }

                    results.append(result)

                return results
        except Exception as e:
            logging.error("error in duckduckgo search", str(e))
            logging.error("full error details", type(e).__name__)
            return []

    async def generate_talking_points(self, session: dict[str, Any]) -> str | None:
        logging.info("init generate talking points")

        try:

            human_msg_content = (
                f"<User Input> \n {session.get('research_topic')} \n <User Input>\n\n"
                f"<Search Summary> \n {session.get('running_summary')} \n <Search Summary>"
            )

            result = await self.llm_reasoning.ainvoke(
                [
                    SystemMessage(
                        content=talking_points_instructions.format(
                            research_topic=session.get("research_topic")
                        )
                    ),
                    HumanMessage(content=human_msg_content),
                ]
            )
            talking_points = result.content

            # deepseek specific
            # leave think parts in the talking points withdeepseek. hopefully the think helps
            # the next model to come up with a good podcast script

            # if (
            #     "deepseek" in Config.local_llm
            #     or "deepseek" in Config.local_llm_reasoning
            # ):
            #     while "<think>" in talking_points and "</think" in talking_points:
            #         # remove think section from the final output
            #         start = talking_points.find("<think>")
            #         end = talking_points.find("</think>") + len("</think>")
            #         talking_points = talking_points[:start] + talking_points[end:]

            return talking_points

        except Exception as e:
            logging.error("error in generating talking points", str(e))

    async def fetch_url_content(
        self, client_session: dict[str, Any], TARGET_URL: str
    ) -> str:
        try:

            async def fetch(session: ClientSession, url):
                async with session.get(url) as response:
                    return await response.text()

            async def parse(client_session: dict[str, Any], html):
                soup = BeautifulSoup(html, "html.parser")
                all_text = soup.get_text(separator=" ", strip=True)
                cleaned_text = re.sub(r"\s+", " ", all_text)

                logging.info("init content extraction")
                try:
                    human_msg_content = (
                        f"<User Input> \n {client_session.get('research_topic')} \n <User Input>\n\n"
                        f"<HTML Page Content> \n {cleaned_text} \n <HTML Page Content>"
                    )

                    result = await self.llm.ainvoke(
                        [
                            SystemMessage(
                                content=content_extraction_instructions.format(
                                    research_topic=session.get("research_topic")
                                )
                            ),
                            HumanMessage(content=human_msg_content),
                        ]
                    )
                    content_extracted = result.content

                    # deepseek specific
                    if (
                        "deepseek" in Config.local_llm
                        or "deepseek" in Config.local_llm_reasoning
                    ):
                        while (
                            "<think>" in content_extracted
                            and "</think" in content_extracted
                        ):
                            # remove think section from the final output
                            start = content_extracted.find("<think>")
                            end = content_extracted.find("</think>") + len("</think>")
                            content_extracted = (
                                content_extracted[:start] + content_extracted[end:]
                            )

                    return content_extracted
                except Exception as e:
                    logging.error(f"Error extracting content '{TARGET_URL}': {str(e)}")
                    return ""

            # --- fetch url and parse content with llm
            async with aiohttp.ClientSession() as session:
                html = await fetch(session, TARGET_URL)
                return await parse(client_session, html)
        except Exception as e:
            logging.error(f"Error crawling the web '{TARGET_URL}': {str(e)}")
            return ""

    async def embed_url(
        self, client_session: dict[str, Any], TARGET_URL: str, session_id: str
    ) -> str:
        try:
            fetched_content = await self.fetch_url_content(
                client_session=client_session, TARGET_URL=TARGET_URL
            )
            if len(fetched_content) > 0:
                logging.info("not empty content")
                # add to vectorDB for sessionid for later questioning knowledge
                document = Document(
                    page_content=fetched_content, metadata={"source": TARGET_URL}
                )
                documents: Iterable[Document] = [document]

                if documents:
                    logging.info("embedding content to vectordb")
                    # split text
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=1000, chunk_overlap=200
                    )
                    documents = text_splitter.split_documents(documents)

                    # Create embeddings
                    embeddings = HuggingFaceEmbeddings(
                        model_name=Config.HF_EMBEDDINGS_MODEL_NAME
                    )

                    vectordb = Chroma.from_documents(
                        documents=documents,
                        embedding=embeddings,
                        persist_directory=Config.INDEX_PERSIST_DIRECTORY,
                        collection_name=session_id,
                    )
                    vectordb.persist()

                    logging.info("content persisted in vectordb")

            return fetched_content
        except Exception as e:
            logging.error("failed fetch_url_content", str(e))
        return ""
