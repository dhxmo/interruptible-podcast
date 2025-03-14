import unittest
import asyncio

from AIR.src.deep_research.search import DeepResearcher
from AIR.src.manager import ClientManager


class AIRTestCasesUnit(unittest.TestCase):
    def setUp(self):
        self.dr = DeepResearcher()
        self.cm = ClientManager()
        self.session_id = self.cm.create_session()

    def test_finalize_report(self):
        pass

    # --- input prompt to talking points + RAG
    def test_deep_research_report(self):
        return asyncio.run(self._ds_report())

    async def _ds_report(self):
        user_input = "find out about quantum computing"

        research_summary = await self.dr.generate_report(
            user_input, self.cm.sessions[self.session_id]
        )

        print("result", research_summary)
        self.assertGreater(len(research_summary), 0)

    def test_podcast_talking_points_output(self):
        research_report = """

        """

        talking_points = self.dr.generate_talking_points(research_report)

        print("talking_points", talking_points)

        self.assertGreater(len(talking_points), 0)

    def test_generate_long_form_with_report_n_talking_points(self):
        # podcastify content generator generate_long_form
        # different personality to [MAN] and [WOMAN]
        pass

    def test_split_pod_text_to_different_voices(self):
        pass

    def test_answer_user_query_n_continue_generate_long_form_using_talking_points(self):
        pass

    # --- human audio to response
    def test_stt(self):
        pass


if __name__ == "__main__":
    unittest.main()
