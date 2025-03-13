import logging
import re
from typing import Iterable

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlResult, LXMLWebScrapingStrategy
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel

from .util import clean_markdown
from ..config import Config


class Query(BaseModel):
    topic: str
    response: str


class WebCrawler:
    async def crawl_web(
        self, link: str, topic: str, is_local: bool = True
    ) -> CrawlResult:
        return await self._crawl(link, topic, is_local)

    async def _crawl(
        self, link: str, topic: str, is_local: bool = True
    ) -> CrawlResult | None:
        llm_strategy = LLMExtractionStrategy(
            llmConfig=LLMConfig(provider=f"ollama/{Config.local_llm}", api_token=None),
            schema=Query.model_json_schema(),
            extraction_type="schema",
            instruction=f"Extract all information related to {topic} from the content.",
            chunk_token_threshold=1000,
            overlap_rate=0.0,
            apply_chunking=True,
            input_format="markdown",
            extra_args={"temperature": 0.0, "max_tokens": 800},
        )

        browser_config = BrowserConfig()  # Default browser configuration
        run_config = CrawlerRunConfig(
            # Content filtering
            word_count_threshold=10,
            excluded_tags=["form", "header", "footer", "img", "a", "nav"],
            exclude_external_links=True,  # Remove external links
            keep_data_attributes=False,
            # Content processing
            remove_overlay_elements=True,  # Remove popups/modals
            process_iframes=False,  # Process iframe content
            # Cache control
            cache_mode=CacheMode.ENABLED,  # Use cache if available
            scraping_strategy=LXMLWebScrapingStrategy(),
            exclude_social_media_links=True,
            page_timeout=5000,
        )

        if is_local:
            try:
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    result = await crawler.arun(
                        url=link, config=run_config, extraction_strategy=llm_strategy
                    )

                    if not result.success:
                        logging.error(f"Crawl failed: {result.error_message}")
                        logging.error(f"Status code: {result.status_code}")
                        return None
                    else:
                        return result
            except Exception as e:
                logging.error(f"Error crawling the web '{link}': {str(e)}")
                raise

    @staticmethod
    def post_process_text(content):
        # Removing Square Brackets and Extra Spaces
        article_text = re.sub(r"\[[0-9]*\]", " ", content)
        article_text = re.sub(r"\s+", " ", article_text)
        # Removing special characters and digits
        formatted_article_text = re.sub("[^a-zA-Z]", " ", article_text)
        formatted_article_text = re.sub(r"\s+", " ", formatted_article_text)

        return article_text, formatted_article_text


async def fetch_url_content(TARGET_URL: str, topic: str) -> str:
    try:
        crawler = WebCrawler()
        crawled_data = await crawler.crawl_web(link=TARGET_URL, topic=topic)

        if crawled_data:
            md = clean_markdown(crawled_data.markdown)

            if len(crawled_data.markdown) > 200:
                logging.info("markdown fetched for url", TARGET_URL)
                return md
            return ""
        return ""
    except Exception as e:
        logging.error(f"Error crawling the web '{TARGET_URL}': {str(e)}")
        return ""


async def embed_url(TARGET_URL: str, topic: str, session_id: str) -> str:
    try:
        md = await fetch_url_content(TARGET_URL, topic)

        # add to vectorDB for sessionid for later questioning knowledge
        document = Document(page_content=md, metadata={"source": TARGET_URL})
        documents: Iterable[Document] = [document]

        if documents:
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

            return md
        return ""
    except Exception as e:
        logging.error("failed fetch_url_content", str(e))
    return ""
