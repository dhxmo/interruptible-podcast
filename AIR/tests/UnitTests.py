import asyncio
import unittest

from AIR.src.deep_research.search import DeepResearcher
from AIR.src.manager import ClientManager
from AIR.src.pod_gen.generate import PodGenStandard
from AIR.src.pod_gen.pg_templates import rag_flow_prompt
from AIR.src.tts.speech_gen import SpeechGen
from AIR.src.whisper import FasterWhisperEngine


class AIRTestCasesUnit(unittest.TestCase):
    def setUp(self):
        self.dr = DeepResearcher()
        self.cm = ClientManager()
        self.session_id = self.cm.create_session()
        self.pg = PodGenStandard()
        self.stt = FasterWhisperEngine()
        self.tts = SpeechGen()

    # --- human audio transcribe
    def test_stt(self):
        # TODO: file input for testing. in main, stream audio and save as buffer, pass buffer directly to function
        full_text = self.stt.transcribe(
            self.cm.sessions[self.session_id], "./data/male.wav"
        )

        self.assertGreater(len(full_text), 0)

    # --- deep search based on user query
    def test_web_search_n_scrape(self):
        return asyncio.run(self._web_search_n_scrape())

    async def _web_search_n_scrape(self):
        search_result = await self.dr.web_search_n_scrape(
            self.cm.sessions[self.session_id], "quantum computing"
        )
        self.assertGreater(len(search_result), 0)

    # --- input prompt to talking points
    def test_deep_research_report(self):
        return asyncio.run(self._ds_report())

    async def _ds_report(self):
        user_input = "tell me whats latest in quantum computing"

        talking_points = await self.dr.generate_report(
            user_input, self.cm.sessions[self.session_id]
        )

        print("\n\ntalking points:", talking_points)

        print(
            "\n\nrunning summary", self.cm.sessions[self.session_id]["running_summary"]
        )

        self.assertGreater(len(talking_points), 0)

    # --- TODO: generate conversation based on talking points
    def test_generate_with_summary_talking_points(self):
        asyncio.run(self._podgen())

    async def _podgen(self):
        talking_points = ""

        self.cm.sessions[self.session_id]["running_summary"] = ""

        script = await self.pg.podgen(
            self.cm.sessions[self.session_id],
            talking_points,
        )

        self.assertGreater(len(script), 0)


if __name__ == "__main__":
    unittest.main()
