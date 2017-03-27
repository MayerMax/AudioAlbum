from album import Album
import unittest
import os.path


class TestAlbum(unittest.TestCase):

    def setting_up_album(self, path=''):
        return Album(album_path=path)

    # Album is reference object type
    def procedd_fingerprints(self, album):
        album.setup_album()
        album.proceed_fingerprints()

    def test_setup_album(self):
        path = os.path.join('audio', 'set2')
        album = self.setting_up_album(path)
        managed_to_set = album.setup_album()
        self.assertTrue(managed_to_set)
        self.assertEqual(len(album.songs), 1)
        self.assertEqual(album.songs[0].information, False)

    def test_check_how_it_prints(self):
        path = os.path.join('audio', 'set2')
        album = self.setting_up_album(path)
        album.setup_album()
        self.assertEqual(len(album.songs), 1)
        album.show_album()
        # [audio\set2\demo1.mp3 frame rate 22050 with 2 channel,
        # some info: False]

    def test_proceed_album(self):
        album = self.setting_up_album(os.path.join('audio', 'set2'))
        self.procedd_fingerprints(album)
        self.assertTrue(1000 < len(album.songs[0].dict_of_hashes) < 5000)

    def test_unique_song_insertion(self):
        album = self.setting_up_album(os.path.join('audio', 'set2'))
        self.procedd_fingerprints(album)

        path_to_song2 = os.path.join('finger_print', 'demo1_frag.mp3')
        boolean, name = album.insert_song(path_to_song2)
        self.assertEqual(boolean, True)
        self.assertTrue(len(album.songs) == 2)

    def test_duplicates_song_insertion(self):
        album = self.setting_up_album(os.path.join('audio', 'set2'))
        self.procedd_fingerprints(album)

        path_to_song2 = os.path.join('audio', 'set2', 'demo1.mp3')
        boolean, name = album.insert_song(path_to_song2)
        self.assertEqual(boolean, False)
        self.assertTrue(len(album.songs), 1)

    def test_predict_complete_result(self):
        album = self.setting_up_album(os.path.join('audio', 'set2'))
        self.procedd_fingerprints(album)

        path_to_song = os.path.join('finger_print', 'demo1_frag.mp3')

        counts, name = album.predict_song(path_to_song)
        self.assertEqual(name, 'audio\set2\demo1.mp3')
        self.assertTrue( 10 < counts < 100)

    def test_predict_no_matches(self):
        album = self.setting_up_album(os.path.join('audio', 'set2'))
        self.procedd_fingerprints(album)

        path_to_song = os.path.join('finger_print', 'unknown_fragment_2.mp3')
        counts, name = album.predict_song(path_to_song)
        self.assertEqual(counts, 0)
        self.assertEqual(name, 'Empty')

