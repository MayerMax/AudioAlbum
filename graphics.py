import datetime
import wx
import wx.lib.scrolledpanel
import wx.lib.agw.gradientbutton as GB
import wx.lib.buttons as buttons
import wx.media
import os
from album import Album
from multiprocessing.pool import ThreadPool

DEFAULT_DIR = os.path.dirname(os.path.abspath(__file__))
BIT_MAP_DIR = os.path.join(DEFAULT_DIR, 'assets')


class AudioAlbum(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title,
                          style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)

        self.album_panel = wx.lib.scrolledpanel.ScrolledPanel(
            self,
            -1,
            size=(1020, 600),
            pos=(0, 0),
            style=wx.SIMPLE_BORDER)

        # self.album_panel.SetupScrolling()

        self.player_panel = wx.Panel(
            self,
            style=wx.SUNKEN_BORDER,
            size=(1020, 100),
            pos=(0, 600))

        self.album_panel.SetBackgroundColour('#643a3e')
        self.player_panel.SetBackgroundColour('#ae9086')

        # current folder setting
        self.current_folder = DEFAULT_DIR
        # end of current folder setting

        self.create_menu_bar()

        # initialize song zone
        self.album = None
        # end of initializing song zone

        # ! -- initialize all attributes for album process
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._update_process, self.timer)
        self.async_result = None
        # --! end of initializing

        # ! -- initialize all attributes for insertion process
        self.second_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._update_insertion, self.second_timer)
        self.async_insertion = None
        # -- ! end of initializing

        # ! -- initialize all attributes for recognizing process
        self.third_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._update_recognize, self.third_timer)
        self.async_recognize = None
        # -- ! end of initializing

        # !-- setting up player
        self.media_player = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER)
        self.song_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer, self.song_timer)
        self.song_timer.Start(100)
        # -- ! end of setting

        # !-- setting current song name available in player
        self.song_text = wx.StaticText(
            self.player_panel,
            label="Edit",
            pos=(500, 0)
        )
        self.font = wx.Font(
            10,
            wx.FONTFAMILY_ROMAN,
            wx.FONTSTYLE_SLANT,
            wx.FONTWEIGHT_NORMAL)
        # self.song_text.SetFont(self.font)

        self.song_len_slider = wx.Slider(
            self.player_panel,
            size=(900, -1),
            pos=(50, 24))

        self.length = wx.StaticText(
            self.player_panel,
            label="00:00",
            pos=(955, 10))

        self.Bind(wx.EVT_SLIDER, self.skip, self.song_len_slider)

        self.play_pause_toggle = self._create_toggle()
        # ending player setting

    def create_menu_bar(self):
        menu_bar = wx.MenuBar()
        # ! -- menu buttons itself
        file_menu = wx.Menu()
        fingerprint_menu = wx.Menu()
        # ! -- end of menus here

        create_album = file_menu.Append(wx.NewId(), "Create Album")
        insert_song = file_menu.Append(wx.NewId(), "Insert Song")
        back_to_album = file_menu.Append(wx.NewId(), "Back to Album")

        recognize_song = fingerprint_menu.Append(wx.NewId(), "Recognize")

        menu_bar.Append(file_menu, "Functions")
        menu_bar.Append(fingerprint_menu, "Extras")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.browsing, create_album)
        self.Bind(wx.EVT_MENU, self.inserting, insert_song)
        self.Bind(wx.EVT_MENU, self.back, back_to_album)

        self.Bind(wx.EVT_MENU, self.recognize, recognize_song)

    def _create_toggle(self):
        img = wx.Bitmap(os.path.join(BIT_MAP_DIR, "play.png"))
        stop_img = wx.Bitmap(os.path.join(BIT_MAP_DIR, 'stop.png'))
        button = buttons.GenBitmapToggleButton(
            self.player_panel,
            bitmap=img,
            name="play",
            pos=(0, 5),
            size=(3, 3)
        )

        button.Enable(False)
        button.SetBitmapSelected(stop_img)
        button.SetInitialSize()
        button.Bind(wx.EVT_BUTTON, self.play)
        return button

    def _on_timer(self, event):
        try:
            offset = self.media_player.Tell()
            if offset > 0:
                cur_place = datetime.datetime.fromtimestamp(offset / 1000.0)
                m = str(cur_place.minute)
                s = str(cur_place.second)
                minutes = cur_place.minute if cur_place.minute > 0 else '0' + m
                seconds = cur_place.second if cur_place.second > 9 else '0' + s

                self.length.SetLabel(str(minutes) + ":" + str(seconds))
            else:
                self.length.SetLabel("00:00")
            text = self.song_text.GetLabel()

            self.song_text.SetLabel(label=text)
            self.song_text.SetPosition(pt=(500, 0))
            self.song_len_slider.SetValue(offset)
        except RuntimeError:
            'caught exception'

    def skip(self, event):
        offset = self.song_len_slider.GetValue()
        self.media_player.Seek(offset)

    def play(self, event):
        if not event.GetIsDown():
            self.pause()
            return
        else:
            self.media_player.SetInitialSize()
            self.song_len_slider.SetRange(0, self.media_player.Length())
            self.media_player.Play()

        event.Skip()

    def pause(self):
        self.media_player.Pause()

    # AREA FOR FUNCTIONALITY !!!
    def browsing(self, event):
        formats = "MP3 (*.mp3)|*.mp3"
        if self.album:
            wx.MessageBox(
                "Sorry, you've instantiated album, "
                "you can now only Insert Tracks")
            return

        dialog = wx.FileDialog(self,
                               message="Open folder",
                               defaultDir=self.current_folder,
                               defaultFile="",
                               wildcard=formats
                               )
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            self.current_folder = os.path.dirname(path)
            self.album = Album(album_path=self.current_folder)

            pool = ThreadPool(processes=1)
            self.timer.Start(1000)
            self.async_result = pool.apply_async(
                self.album.setup_album,
                (None,))
            wx.MessageBox('Now I am fingerprinting in'
                          'sight mode, it takes time, but you can continue '
                          'listening')

    def inserting(self, event):
        formats = "MP3 (*.mp3)|*.mp3"
        if not self.album:
            wx.MessageBox('Sorry, but before you should create album')
            return
        dialog = wx.FileDialog(
            self,
            defaultDir=self.current_folder,
            defaultFile="",
            wildcard=formats)

        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            self.current_folder = os.path.dirname(path)
            pool = ThreadPool(processes=1)
            self.second_timer.Start(1000)
            self.async_insertion = pool.apply_async(
                self.album.insert_song,
                (path,))
            wx.MessageBox('Now I am adding a song and fingerprinting it in'
                          'sight mode, it takes time, but you can continue '
                          'listening')

    def recognize(self, event):
        self._clear_panel()
        formats = "MP3 (*.mp3)|*.mp3"
        if not self.album:
            wx.MessageBox('Sorry, but your data base is not cooked!')
            return
        wx.MessageBox('It works obviously!')

        dialog = wx.FileDialog(
            self,
            defaultDir=self.current_folder,
            defaultFile="",
            wildcard=formats)

        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            self.current_folder = os.path.dirname(path)
            pool = ThreadPool(processes=1)
            self.third_timer.Start(1000)
            self.async_recognize = pool.apply_async(
                self.album.predict_song,
                (path,))
            wx.MessageBox("I am searching for a result! Wait please")

            button = self._button_construction( # noqa
                label=path,
                size=(200, 200),
                pos=(200, 200)
            )

            text = wx.StaticText( # noqa
                self.player_panel,
                label="Edit",
                pos=(600, 200)
            )

    def back(self, event):
        self._clear_panel()
        if self.album:
            self.generate_album_buttons()
            return
        else:
            wx.MessageBox('First, Instantiate the Album!')
    # END OF FUNCTIONALITY AREA !!!

    # ZONE for few thread functions
    def _update_process(self, event):
        if self.async_result and self.async_result.ready():
            self.generate_album_buttons()
            self.async_result = None
            wx.MessageBox('I ve added them, and Clastered')

    def _update_insertion(self, event):
        if self.async_insertion and self.async_insertion.ready():
            insert_result = self.async_insertion.get()
            self.async_insertion = None
            if not insert_result[0]:
                explain = 'Sorry this is yet here ' + str(insert_result[1])

                wx.MessageBox(explain)

            else:
                self.generate_album_buttons()
                explain = 'Cool, this is added!'
                # self.async_insertion = None
                wx.MessageBox(explain)

    def _update_recognize(self, event):
        if self.async_recognize and self.async_recognize.ready():
            result = self.async_recognize.get()
            self.async_recognize = None
            if result[0] == 0:
                wx.MessageBox('Sorry, No matches!')
            else:
                times = result[0]
                name = result[1]
                button = self._button_construction( # noqa
                    label=name,
                    size=(200, 200),
                    pos=(600, 200)
                )
                wx.MessageBox('This is probably this song with\n' + str(times)
                              + ' Matches from database')

    # ENDING OF ZONE for thread functions
    def _extend_library(self, new_songs):
        for song in new_songs:
            if song not in self.album:
                self.album.append(song)

    def _clear_panel(self):
        for child in self.album_panel.GetChildren():
            child.Destroy()

    def generate_album_buttons(self):
        index = 1
        x = 0
        y = 0
        const_size = 190
        const_size_y = 70
        offset = 200
        general_sizer = wx.BoxSizer(wx.VERTICAL)
        side_sizer = wx.BoxSizer(wx.HORIZONTAL)

        for song in self.album.songs:
            if index == 5:
                button = self._button_construction(
                    label=song.name,
                    size=(const_size, const_size_y),
                    pos=(x, y))
                index = 1
                y += const_size_y + 10
                x = 0
                side_sizer.Add(button)
                general_sizer.Add(side_sizer)
                side_sizer = wx.BoxSizer(wx.HORIZONTAL)

            else:
                button = self._button_construction(
                    label=song.name,
                    size=(const_size, const_size_y),
                    pos=(x, y))
                side_sizer.Add(button)
                x += offset + 2
                index += 1
        self.album_panel.SetSizer(general_sizer)

    def _button_construction(self, label, size, pos):
        slash_index = label.rindex("\\")
        if slash_index != -1:
            name = label[slash_index + 1:len(label)]
            name = name[0:22]
        else:
            name = label[0:len(label) - 5]

        bmp = wx.Bitmap(
            os.path.join(BIT_MAP_DIR, "agt_mp3.png"),
            wx.BITMAP_TYPE_ANY)

        button = GB.GradientButton(
            self.album_panel,
            bitmap=bmp,
            id=wx.ID_ANY,
            label=str("\n") + name,
            size=size,
            pos=pos,
            name=label)
        button.Bind(wx.EVT_BUTTON, self.load_song)
        return button

    def load_song(self, event):
        button = event.GetEventObject()
        self.media_player.Stop()
        self.play_pause_toggle.SetValue(False)
        self.media_player.Load(button.GetName())

        self.play_pause_toggle.Enable(True)
        self.song_text.SetLabel(label=button.GetLabel())
        # self.song_text.SetPosition(pt=(500, 5))

if __name__ == '__main__':
    app = wx.App(False)
    form = AudioAlbum(None, 'Audio')
    form.SetSize((1020, 700))
    form.Show()
    app.SetTopWindow(form)
    app.MainLoop()
