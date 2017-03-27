import os
from readingfiles import FileReader
from multiprocessing.dummy import Pool as ThreadPool
from music import receive_fingerprints


class Album:
    def __init__(self, album_path):
        self.root = album_path
        self.songs = None

    def setup_album(self, args=None):
        reader = FileReader(directory=os.path.join(self.root))
        self.songs = reader.forming_a_song_library()
        self.proceed_fingerprints()
        return True

    # only for debug or human way looking it
    def show_album(self):
        print(self.songs)

    def proceed_fingerprints(self, args=None):
        pool = ThreadPool(4)
        pool.map(receive_fingerprints, self.songs)
        pool.close()
        pool.join()

    def insert_song(self, song_path):
        reader = FileReader(directory='')
        new_song = reader.review_music_file(path_file=song_path)
        for song in self.songs:
            if new_song.static_hash == song.static_hash:
                return False, song.name
        receive_fingerprints(new_song)
        self.songs.append(new_song)

        return True, new_song.name

    @staticmethod
    def cook_song_with_fingerprint(song_path):
        reader = FileReader(directory='')
        song = reader.review_music_file(path_file=song_path)
        receive_fingerprints(song)
        return song

    # receive a song exactly, with it's own static hash!
    def light_predictor(self, unknown_song):
        for song in self.songs:
            if song.static_hash == unknown_song.static_hash:
                return len(song.dict_of_hashes.keys()), song.name
        return False

    @staticmethod
    def _create_relative_matches(song_hashes, unknown_song_hashes):
        list_of_matches = []
        for finger_print in song_hashes.keys():
            if finger_print in unknown_song_hashes.keys():
                song_moment = song_hashes[finger_print]
                unknown_song_moment = unknown_song_hashes[finger_print]
                diff = abs(song_moment - unknown_song_moment)
                list_of_matches.append(diff)
        return list_of_matches

    def predict_song(self, unknown_song):
        if not isinstance(unknown_song, type(self.songs[0])):
            unknown_song = Album.cook_song_with_fingerprint(unknown_song)
            unknown_song_hashes = unknown_song.dict_of_hashes
        else:
            unknown_song_hashes = unknown_song.dict_of_hashes

        light_compare = self.light_predictor(unknown_song)
        if light_compare:
            return light_compare

        relative_results = dict()
        for song in self.songs:
            song_hashes = song.dict_of_hashes
            relative_results[song.name] = Album._create_relative_matches(
                song_hashes,
                unknown_song_hashes
            )
            # for finger_print in song_hashes.keys():
            #     if finger_print in unknown_song_hashes.keys():
            #         song_moment = song_hashes[finger_print]
            #         unknown_song_moment = unknown_song_hashes[finger_print]
            #         diff = abs(song_moment - unknown_song_moment)
            #
            #         relative_results[song.name].append(diff)

        prediction = dict()
        for song in self.songs:
            prediction[song.name] = 0
            song_hashes = song.dict_of_hashes
            time_line_result = relative_results[song.name]
            # for finger_print in song_hashes.keys():
            #     if song_hashes[finger_print] in relative_results[song.name]:
            #         prediction[song.name] += 1
            prediction[song.name] = Album._align_fragment_with_song(
                song_hashes,
                time_line_result)

        maximum = 0
        name = ""
        for match in prediction.keys():
            if prediction[match] > maximum:
                maximum = prediction[match]
                name = match

        if name in prediction.keys():
            return prediction[name], name
        else:
            return 0, "Empty"

    @staticmethod
    def _align_fragment_with_song(song_hashes, relative_results_time):
        counts = 0
        for finger_print in song_hashes.keys():
            if song_hashes[finger_print] in relative_results_time:
                counts += 1
        return counts


