import logging
import re
from typing import List


class ContentCleanerMixin:
    """
    Mixin class containing common transcript cleaning operations.

    Provides reusable cleaning methods that can be used by different content generation strategies.
    Methods use protected naming convention (_method_name) as they are intended for internal use
    by the strategies.
    """

    @staticmethod
    def _clean_scratchpad(text: str) -> str:
        """
        Remove scratchpad blocks, plaintext blocks, standalone triple backticks, any string enclosed in brackets, and underscores around words.
        """
        try:
            import re

            pattern = r"```scratchpad\n.*?```\n?|```plaintext\n.*?```\n?|```\n?|\[.*?\]"
            cleaned_text = re.sub(pattern, "", text, flags=re.DOTALL)
            # Remove "xml" if followed by </Person1> or </Person2>
            cleaned_text = re.sub(r"xml(?=\s*</Person[12]>)", "", cleaned_text)
            # Remove underscores around words
            cleaned_text = re.sub(r"_(.*?)_", r"\1", cleaned_text)
            return cleaned_text.strip()
        except Exception as e:
            logging.error(f"Error cleaning scratchpad content: {str(e)}")
            return text

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
