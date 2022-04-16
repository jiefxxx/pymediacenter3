import sys
import time

import vlc
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtWidgets import QFrame, QDialog, QDialogButtonBox, QVBoxLayout, QLabel

PLAYER_STATE_IDLE = 0
PLAYER_STATE_PLAYING = 1
PLAYER_STATE_PAUSED = 2


class ConfirmationDialog(QDialog):

    def __init__(self, string, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        self.setWindowTitle("need confirmation")

        end_button = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.layout = QVBoxLayout()

        self.label = QLabel(string)

        self.buttonBox = QDialogButtonBox(end_button)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class Player(QFrame):
    position_changed = pyqtSignal('PyQt_PyObject')
    state_changed = pyqtSignal('PyQt_PyObject')
    media_changed = pyqtSignal('PyQt_PyObject')
    media_finished = pyqtSignal()

    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.model_manager = parent.model_manager
        self.instance = vlc.Instance()

        self.media_player = self.instance.media_player_new()
        self.media_player.video_set_mouse_input(0)
        self.media_player.video_set_key_input(0)

        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.media_player.set_xwindow(self.winId())
        elif sys.platform == "win32":  # for Windows
            self.media_player.set_hwnd(self.winId())

        events = self.media_player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerEndReached, self.finish_handler)
        self.media_finished.connect(self.on_media_finished)

        self.playlist = []
        self.current = -1

        self.state = PLAYER_STATE_IDLE
        self.state_changed.emit(PLAYER_STATE_IDLE)

        self.timer_timestamp = QTimer(self)
        self.timer_timestamp.setInterval(3 * 60 * 1000)
        self.timer_timestamp.timeout.connect(self.update_timestamp)
        self.timer_timestamp.start()

        self.timer_position = QTimer(self)
        self.timer_position.setInterval(1000)
        self.timer_position.timeout.connect(self.update_position)
        self.timer_position.start()

        self.setFocusPolicy(Qt.NoFocus)
        self.setAutoFillBackground(True)
        self.setMouseTracking(True)

    def finish_handler(self, event):
        self.media_finished.emit()

    def on_media_finished(self):
        if self.current < len(self.playlist):
            self.next()
        else:
            self.stop()

    def update_timestamp(self):
        if self.state == PLAYER_STATE_PLAYING:
            self.model_manager.server.set_watch_time(self.playlist[self.current]["id"], int(self.media_player.get_time()))

    def update_position(self):
        if self.state == PLAYER_STATE_PLAYING:
            info = {}
            info["position"] = self.media_player.get_position()
            info["total_time"] = int(self.media_player.get_length())
            info["current_time"] = int(self.media_player.get_time())
            self.position_changed.emit(info)

    def play(self, play=None):
        if self.media_player.is_playing() and not play:
            self.media_player.pause()
            self.update_timestamp()
            self.state = PLAYER_STATE_PAUSED
            self.state_changed.emit(PLAYER_STATE_PAUSED)
        elif play or play is None:
            self.media_player.play()
            self.update_position()
            self.state = PLAYER_STATE_PLAYING
            self.state_changed.emit(PLAYER_STATE_PLAYING)

    def stop(self):
        self.update_timestamp()
        self.media_player.stop()
        self.state = PLAYER_STATE_IDLE
        self.state_changed.emit(PLAYER_STATE_IDLE)
        info = {}
        info["position"] = 0
        info["total_time"] = 0
        info["current_time"] = 0
        self.position_changed.emit(info)
        self.playlist = []
        self.current = -1

    def next(self, inc_factor=1):
        if self.state == PLAYER_STATE_PLAYING:
            self.play()

        self.current += inc_factor
        if self.current < 0:
            self.current = 0
        elif self.current >= len(self.playlist):
            self.current = len(self.playlist)-1

        self.load()

    def previous(self):
        self.next(-1)

    def set_playlist(self, playlist):
        if self.state == PLAYER_STATE_PLAYING:
            self.play()

        self.playlist = playlist
        self.current = 0

        self.load()

    def load(self):
        media = self.instance.media_new(self.playlist[self.current]["stream_path"])
        self.media_player.set_media(media)
        self.media_changed.emit(self.playlist[self.current]["info"])
        self.play(True)

        while not self.media_player.is_playing():   # wait to get data
            pass

        for track in self.media_player.audio_get_track_description():   # set track français
            if track[1].decode().split("[")[-1][:-1] == "Français":
                self.media_player.audio_set_track(track[0])

        timestamp = self.playlist[self.current]["watch_time"]
        if timestamp is not None and timestamp < (self.media_player.get_length()*0.9):  # set timestamp
            self.media_player.set_time(timestamp)

    def set_position(self, position):
        self.timer_position.stop()
        self.media_player.set_position(position)
        self.update_position()
        self.timer_position.start()

    def inc_time(self, inc_factor):
        self.timer_position.stop()
        target = self.media_player.get_time() + (inc_factor * 1000)
        if target < 0:
            target = 0
        elif target > self.media_player.get_length():
            target = self.media_player.get_length()-1
        self.media_player.set_time(target)
        self.update_position()
        self.timer_position.start()

    def set_audio_device(self, device):
        self.media_player.pause()
        self.media_player.audio_output_device_set(None, device)
        time.sleep(0.05)
        self.media_player.pause()

    def set_audio(self, track):
        self.media_player.audio_set_track(track)

    def set_subtitle(self, track):
        self.media_player.video_set_spu(track)

    def set_ratio(self, ratio):
        self.media_player.video_set_aspect_ratio(ratio)

    def set_crop(self, crop):
        self.media_player.video_set_crop_geometry(crop)

    def get_info_crop_ratio(self):
        return {
            "ratio": self.media_player.video_get_aspect_ratio(),
            "crop": self.media_player.video_get_crop_geometry()
        }

    def get_info_str_audio(self):
        devices = []
        mods = self.media_player.audio_output_device_enum()

        if mods:
            mod = mods
            while mod:
                mod = mod.contents
                devices.append(mod.device)
                mod = mod.next

        vlc.libvlc_audio_output_device_list_release(mods)
        audios = self.media_player.audio_get_track_description()
        subtitles = self.media_player.video_get_spu_description()
        return {
            "Devices": devices,
            "Audios": audios,
            "Audios-selected": self.media_player.audio_get_track(),
            "Subtitles": subtitles,
            "Subtitles-selected": self.media_player.video_get_spu()
        }









