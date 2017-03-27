from pydub import AudioSegment
from music import Song
import fnmatch
import numpy as np
import os
import hashlib
from multiprocessing.pool import ThreadPool


class FileReader:
    def __init__(self, directory=None):
        self.working_directory = directory
        self.audio_file = None

    def read(self, file_name):
        self.audio_file = AudioSegment.from_file(file_name)

        data = np.fromstring(self.audio_file._data, np.int16)
        channels = []
        for channel in range(self.audio_file.channels):
            channels.append(data[channel::self.audio_file.channels])

        return self.audio_file.frame_rate, channels

    def review_directory(self):
        music_only = []
        extensions = ['*.mp3']
        for dir_path, dir_list, dir_files in os.walk(self.working_directory):
            for extension in extensions:
                with_path = [os.path.join(dir_path, file) for file in
                             dir_files]
                curr_music = fnmatch.filter(with_path, extension)
                music_only.extend(curr_music)
        return music_only

    def review_music_file(self, path_file):
        frame_rate, channels = self.read(file_name=path_file)
        song_hash = FileReader.hash_file_static(path=path_file)
        probable_tags = FileReader.id_tags(file=path_file)

        return Song(path_file, frame_rate, channels, song_hash, probable_tags)

    @staticmethod
    def hash_file_static(path, block_size=65536):
        with open(path, 'rb') as file:
            hash_func = hashlib.md5()
            buffer = file.read(block_size)
            while len(buffer) > 0:
                hash_func.update(buffer)
                buffer = file.read(block_size)

        return hash_func.hexdigest()

    def find_unique_files(self, arg=None):
        unique_file = {}
        duplicate_files = []
        list_of_tracks = self.review_directory()
        pool = ThreadPool(processes=1)

        for song_path in list_of_tracks:
            async_result = pool.apply_async(
                FileReader.hash_file_static,
                (song_path, ))

            # unique_hash = FileReader.hash_file_static(path=song_path)
            unique_hash = async_result.get()

            if unique_hash in unique_file.keys():
                duplicate_files.append(song_path)
            else:
                unique_file[unique_hash] = song_path

        return unique_file, duplicate_files

    def forming_a_song_library(self, args=None):
        unique_files, duplicates = self.find_unique_files()
        music_list = []
        for unique_hash in unique_files.keys():
            song_rate, song_channels = \
                self.read(file_name=unique_files[unique_hash])
            id3_tags = FileReader.id_tags(file=unique_files[unique_hash])

            music_list.append(Song(unique_files[unique_hash],
                                   song_rate,
                                   song_channels, unique_hash, id3_tags))

        sorted(music_list, key=lambda song: song.name)
        return music_list

    @staticmethod
    def id_tags(file):
        info = []
        reading_file = open(file, 'rb')
        # supporting only ID3v1 tags
        reading_file.seek(-128, 2)
        tag = reading_file.read(128)
        reading_file.close()
        if len(tag) != 128:
            print('only id3v1 tags!')
            return False
        if tag[0:3] != b'TAG':
            return False
        try:
            info.append(tag[3:33].decode('utf-8'))  # title
            info.append(tag[33:63].decode('utf-8'))  # artist
            info.append(tag[63:97].decode('utf-8'))  # album
            info.append(tag[93:97].decode('utf-8'))  # year
            info.append(tag[97:127].decode('utf-8'))  # comment
            info.append(tag[127])  # genre
        except UnicodeDecodeError:
            return False
        return info
