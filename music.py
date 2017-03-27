from search import FingerPrint

class Song:
    def __init__(self, name, frame_rate, channels, static_hash, info):
        self.name = name
        self.frame_rate = frame_rate
        self.channels = channels
        # if it is a ID3v1 song then it has something extra as info chunk
        self.information = info
        self.static_hash = static_hash
        self.dict_of_hashes = dict()

    def __str__(self):
        return str(self.name) + ' frame rate ' + str(self.frame_rate) + \
               ' with ' + str(len(self.channels)) + ' channel, some info: ' + \
               str(self.information)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.static_hash == other.static_hash

    def __hash__(self):
        return self.static_hash


def receive_fingerprints(song):
    if not isinstance(song, Song):
        return None
    fingerprint = FingerPrint()
    peaks = fingerprint.get_peaks(song.channels[0])

    generator = fingerprint.hashing_fingerprints(peaks)
    if generator:
        for element in generator:
            song.dict_of_hashes[element[0]] = element[1]

