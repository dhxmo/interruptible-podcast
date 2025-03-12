import unittest


class AIRTestCasesUnit(unittest.TestCase):
    # --- input prompt to talking points + RAG
    def test_deep_research_report_rag(self):
        pass

    def test_podcast_talking_points_output(self):
        pass

    def test_generate_talking_points_n_rag(self):
        pass

    def test_generate_long_form_with_context(self):
        # podcastify content generator generate_long_form
        pass

    def test_2_llms_generate_long_form_w_each_other_with_context_n_talking_points_n_rag(
        self,
    ):
        # give each llm a different voice and a different personality
        pass

    # --- human audio to response
    def test_stt(self):
        pass

    def test_split_pod_text_to_different_voices(self):
        pass

    def test_generate_text_from_transcript_n_talking_points(self):
        pass


if __name__ == "__main__":
    unittest.main()
