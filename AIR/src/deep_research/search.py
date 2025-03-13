import asyncio
import json
import logging
from pprint import pprint
from typing import List, Dict, Any, Coroutine

from duckduckgo_search import DDGS
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama

from .crawl4ai import embed_url
from .dr_templates import query_writer_instructions
from .util import deduplicate_and_format_sources
from ..config import Config


class DeepResearcher:
    def __init__(self):
        pass

    async def generate_report(self, user_input: str) -> str | None:
        # generate query
        query = self.generate_query(user_input)

        # TODO: pull and update from ClientManager class
        count = Config.research_loop_count
        while count > 0:
            # TODO: update state to ClientManager
            await self.web_search_n_scrape(query)
            # summarize sources
            # reflect on summary

            count -= 1
        # finalize summary

        pass

    def generate_talking_points(self, research_report):
        pass

    @staticmethod
    def generate_query(user_input: str) -> str | None:
        try:
            query_writer_instructions_formatted = query_writer_instructions.format(
                research_topic=user_input
            )

            llm_json_mode = ChatOllama(
                base_url=Config.ollama_base_url,
                model=Config.local_llm,
                temperature=0,
                format="json",
            )

            result = llm_json_mode.invoke(
                [
                    SystemMessage(content=query_writer_instructions_formatted),
                    HumanMessage(content="Generate a query for web search:"),
                ]
            )
            query = json.loads(result.content)

            return query["query"]
        except Exception as e:
            logging.error("error in generate query", str(e))

    async def web_search_n_scrape(self, search_query: str) -> str | None:
        logging.info("init web search")
        try:
            # --- get search results
            search_results = await self.duckduckgosearch(
                search_query,
                max_results=Config.search_max_results,
            )

            # --- scrape and embed content for reuse later for questioning
            # Create a list of coroutines while maintaining index association
            tasks = [
                embed_url(result["url"], topic=search_query, session_id=Config.uuid)
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

    def summarize_sources(self):
        try:
            pass
        except Exception as e:
            logging.error("error in summarize sources", str(e))

    def reflect(self):
        try:
            pass
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
