import unittest
import asyncio

from AIR.src.deep_research.search import DeepResearcher
from AIR.src.manager import ClientManager


class AIRTestCasesUnit(unittest.TestCase):
    def setUp(self):
        self.dr = DeepResearcher()
        self.cm = ClientManager()
        self.session_id = self.cm.create_session()

    # UNITS for generate report
    # 3 search queries : 172.12s on GPU
    def test_web_search_n_scrape(self):
        return asyncio.run(self._web_search_n_scrape())

    async def _web_search_n_scrape(self):
        search_result = await self.dr.web_search_n_scrape(
            self.cm.sessions[self.session_id], "quantum computing"
        )
        self.assertGreater(len(search_result), 0)

    # --- input prompt to talking points + RAG
    def test_deep_research_report(self):
        return asyncio.run(self._ds_report())

    async def _ds_report(self):
        user_input = "tell me whats latest in quantum computing"

        talking_points = await self.dr.generate_report(
            user_input, self.cm.sessions[self.session_id]
        )

        print("result", talking_points)
        self.assertGreater(len(talking_points), 0)

    def test_generate_long_form_with_report_n_talking_points(self):
        # podcastify content generator generate_long_form
        # different personality to [MAN] and [WOMAN]

        # use talking points and session running summary to generate podcast content
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
