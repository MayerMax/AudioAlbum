import unittest
import os
from readingfiles import FileReader


class TestReadingFiles(unittest.TestCase):

    def create_reader(self, directory):
        return FileReader(directory=os.path.join(directory))

    def test_correct_length(self):
        reader = self.create_reader(directory='audio')
        music = reader.review_directory()
        self.assertEqual(len(music), 6)

    def test_incorrect_tag(self):
        false_tag = FileReader.id_tags(file=os.path.join('audio', 'Drake.mp3'))
        self.assertEqual(false_tag, False)

    def test_correct_tag(self):
        true_tag = FileReader.id_tags(
            file=os.path.join('audio', 'Mirrors.mp3'))
        self.assertTrue(true_tag is not None)

    def test_duplicate_files(self):
        reader = self.create_reader(directory='audio')
        unique_files, duplicates = reader.find_unique_files()
        self.assertEqual(len(unique_files.keys()), 5)
        self.assertEqual(len(duplicates), 1)

    def test_forming_song_library(self):
        reader = self.create_reader(directory='audio')
        starter_album = reader.forming_a_song_library()
        self.assertEqual(len(starter_album), 5)
        self.assertTrue('Calvin.mp3' not in starter_album[0].name)

    def test_is_it_work_with_only_song_not_dir(self):
        form_a_song_path = os.path.join(
            'audio', 'set1', 'Calvin_Duplicate.mp3')
        reader = self.create_reader(directory='')
        song = reader.review_music_file(path_file=form_a_song_path)
        self.assertTrue('Calvin_Duplicate' in song.name)
        self.assertEqual(len(song.information), 6)
        self.assertEqual(len(song.channels), 2)

    def test_static_hash_generator(self):
        path = os.path.join('audio', 'set2', 'demo1.mp3')
        generated_hash = FileReader.hash_file_static(path)
        self.assertEqual(len(generated_hash), 32)