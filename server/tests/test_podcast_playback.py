import os
import unittest

from server.src.core.playback import save_progress, load_progress


class TestPodcastPlayback(unittest.TestCase):
    def setUp(self):
        self.test_progress_file = "test_progress.json"

    def tearDown(self):
        if os.path.exists(self.test_progress_file):
            os.remove(self.test_progress_file)

    def test_save_and_load_progress(self):
        user_id = "uusidh4"
        save_progress(user_id, 3)
        self.assertEqual(load_progress(user_id), 3)
        save_progress(user_id, 0)
        self.assertEqual(load_progress(user_id), 0)

if __name__ == '__main__':
    unittest.main()
