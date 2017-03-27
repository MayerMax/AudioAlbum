import argparse
import wx
from graphics import AudioAlbum
from readingfiles import FileReader
from album import Album


def console_runner():  # noqa
    parser = argparse.ArgumentParser()

    parser.add_argument('-g',
                        '--gui',
                        help='launches program in gui mode',
                        action='store_true')
    parser.add_argument('-i',
                        '--info',
                        help='prints info on song with some specifics',
                        type=str)
    parser.add_argument('-r',
                        '--recognize',
                        help='recognizes [File B] in '
                             'data base given in [Root A]',
                        nargs=2)
    args = parser.parse_args()

    if args.gui:
        app = wx.App(False)
        form = AudioAlbum(None, 'Audio')
        form.SetSize((1020, 700))
        form.Show()
        app.SetTopWindow(form)
        app.MainLoop()

    if args.info:
        try:
            reader = FileReader(directory='')
            song = reader.review_music_file(path_file=args.info)
            print('----Some info on this Song')
            print(song)
            print('----------')

        except FileNotFoundError:
            print('Did not find a path')

    if args.recognize:
        try:
            data_base = args.recognize[0]
            path_to_song = args.recognize[1]
            album = Album(data_base)
            album.setup_album()
            counts, name = album.predict_song(path_to_song)
            print("Using this data_base I found " + name + " Entry")
            print("With " + str(counts) + " Matches")
        except (FileNotFoundError, KeyError) as e:
            print("You have given wrong directory or nonexisting file")

if __name__ == '__main__':
    console_runner()
