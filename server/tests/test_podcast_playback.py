import unittest

from server.src.app.core.genAI.llm import ContentGenerator
from server.src.app.core.genAI.templates import interruption_handle_template


class TestPodcastPlayback(unittest.TestCase):
    def setUp(self):
        self.test_progress_file = "test_progress.json"
        self.llm = ContentGenerator()

    def test_post_interruption_response_generation(self):
        user_input = "will AI take human jobs?"
        next_question = "Today we'll explore how AI is transforming various industries."

        current_context = """
          - **User question**: '{user_input}' 
          - **Next sentence**: '{next_question}' 
        """
        formatted_input = current_context.format(
            user_input=user_input, next_question=next_question
        )

        res = self.llm.generate_content(formatted_input, interruption_handle_template)

        self.assertGreater(len(res), 0)


if __name__ == "__main__":
    unittest.main()
