from typing import List, Dict
import logging
import re


def deduplicate_and_format_sources(
    search_response: List[Dict[str, str]],
    max_tokens_per_response,
    include_raw_content=False,
) -> str:
    """
    Takes either a single search response or list of responses from search APIs and formats them.
    Limits the raw_content to approximately max_tokens_per_source.

    @returns
    formatted_text (str): all sources deduplicated and concat
    """

    # deduplicate urls
    unique_sources = {}
    for src in search_response:
        if src["url"] not in unique_sources:
            unique_sources[src["url"]] = src

    # limit raw_content to max_tokens
    formatted_text = "Sources:\n\n"

    for i, source in enumerate(unique_sources.values(), 1):
        formatted_text += f"Source {source['title']}: \n======\n"
        formatted_text += f"Most relevant content from source: {source['content']} \n\n"

        if include_raw_content:
            char_limit = max_tokens_per_response * 4  # estimated 4 chars per token
            raw_content = source.get("raw_content", "")
            if raw_content is None:
                raw_content = ""
                logging.warning("WARNING: no content found in:", source["url"])
            if len(raw_content) > char_limit:
                raw_content = raw_content[:char_limit] + "...[truncated]"

            formatted_text += f"Full source content limited to {max_tokens_per_response}: {raw_content}\n\n"

    return formatted_text.strip()


def clean_markdown(md_text: str) -> str:
    # Remove YAML front matter (--- at the start and end)
    md_text = re.sub(r"^---\n.*?\n---\n", "", md_text, flags=re.DOTALL)

    # Remove code blocks (both fenced and inline)
    md_text = re.sub(
        r"```.*?```", "", md_text, flags=re.DOTALL
    )  # Remove fenced code blocks
    md_text = re.sub(r"`[^`]+`", "", md_text)  # Remove inline code

    # Remove markdown links but keep the text
    md_text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", md_text)

    # Remove images (markdown format)
    md_text = re.sub(r"!\[.*?\]\(.*?\)", "", md_text)

    # Remove blockquotes
    md_text = re.sub(r"^\s*>+\s?", "", md_text, flags=re.MULTILINE)

    # Remove markdown syntax like **bold**, *italics*, __bold__, _italics_
    md_text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", md_text)  # Bold
    md_text = re.sub(r"(\*|_)(.*?)\1", r"\2", md_text)  # Italics

    # Convert markdown lists into plain text
    md_text = re.sub(r"^\s*[-*+]\s+", "", md_text, flags=re.MULTILINE)  # Bullet lists
    md_text = re.sub(r"^\s*\d+\.\s+", "", md_text, flags=re.MULTILINE)  # Numbered lists

    # Convert markdown headings to plain text
    md_text = re.sub(r"^#+\s*", "", md_text, flags=re.MULTILINE)

    return md_text
