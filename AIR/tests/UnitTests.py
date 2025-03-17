import unittest
import asyncio

from AIR.src.deep_research.dr_templates import talking_points_instructions
from AIR.src.deep_research.search import DeepResearcher
from AIR.src.manager import ClientManager
from AIR.src.pod_gen.generate import PodGen


class AIRTestCasesUnit(unittest.TestCase):
    def setUp(self):
        self.dr = DeepResearcher()
        self.cm = ClientManager()
        self.session_id = self.cm.create_session()
        self.pg = PodGen()

    # TODO: --- human audio to response
    def test_stt(self):
        # transcribe
        # add text to client manager -> input_audio_buffer
        pass

    # --- deep search based on user query
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

        self.assertGreater(len(talking_points), 0)

    # generate podcast script based on talking points
    def test_generate_long_form_with_summary_talking_points(self):
        asyncio.run(self._podgen())

    async def _podgen(self):
        # user_input = "tell me whats latest in quantum computing"
        #
        # talking_points = await self.dr.generate_report(
        #     user_input, self.cm.sessions[self.session_id]
        # )
        #

        talking_points = """ Here are the detailed, engaging talking points for a podcast based on the provided summary:
    
    **1.** **The Quantum Leap: Unveiling Topoconductor**
    What does this world-first quantum processor by Microsoft mean for the future of innovation? How might self-healing materials, sustainable agriculture, and safer chemical discovery become a reality?
    
    **2.** **Breaking Down Barriers: Topological Qubits**
    How did you manage to create your first topological qubit on a chip with one million entangled logical qubits? What challenges did you face, and how did you overcome them?
    
    **3.** **Scaling Up: Building the Quantum Computer of Tomorrow**
    What's the plan for building a scaled quantum computer based on these qubits? How do you envision this technology being used in various industries, and what are the potential applications?
    
    **4.** **Chemistry Made Easier: Hybrid Simulations**
    How will creating 12 logical qubits for hybrid chemistry simulations impact our understanding of chemical reactions and processes? What kind of breakthroughs can we expect from this research?
    
    **5.** **Global Infrastructure: The Future of Quantum Computing**
    As you explore Azure's global infrastructure solutions, what do you see as the key challenges in building a global quantum computing network? How will this technology be accessible to researchers and industries worldwide?"""

        # self.cm.sessions[self.session_id]["running_summary"]
        running_summary = """ The latest developments in quantum computing include the unveiling of a world-first quantum processor called Topoconductor by Microsoft. This breakthrough could lead to innovations like self-healing materials, sustainable agriculture, and safer chemical discovery. The user has already demonstrated their first topological qubit on a chip with one million entangled logical qubits. They are working with Microsoft to build a scaled quantum computer based on these qubits. The user also mentions that they plan to create 12 logical qubits for hybrid chemistry simulations, and have created 12 logical qubits for a hybrid end-to-end chemistry simulation. They are exploring Azure's global infrastructure solutions and looking at creating global infrastructure solutions as well.The latest developments in quantum computing include a world-first quantum processor called Topoconductor by Microsoft, which could lead to innovations like self-healing materials, sustainable agriculture, and safer chemical discovery. The user has demonstrated their first topological qubit on a chip with one million entangled logical qubits. They are working with Microsoft to build a scaled quantum computer based on these qubits. They also plan to create 12 logical qubits for hybrid chemistry simulations and have created 12 logical qubits for a hybrid end-to-end chemistry simulation. The user is exploring Azure's global infrastructure solutions and looking at creating global infrastructure solutions as well."""

        conversational_tone = "Explainer – Simplified breakdowns of complex topics."

        await self.pg.podgen(
            self.cm.sessions[self.session_id],
            running_summary,
            talking_points,
            conversational_tone,
        )

        self.assertGreater(
            self.cm.sessions[self.session_id]["podscript_sentences"].qsize(), 0
        )

    # TODO: --- tts
    def test_tts(self):
        # use kokoro-tts with onnx
        pass

    def test_different_voices_for_different_personality(self):
        # parse text based on [MAN] or [WOMAN]
        # set global in manager and k:v based on that
        pass

    # --- TODO: total
    def test_stream_podcast_script_2_tts_2_client(self):
        pass

    def test_process_interruption_and_stream_contextual_response_back(self):
        # use running summary + embed for session vector db to respond and continue convo
        pass


if __name__ == "__main__":
    unittest.main()
