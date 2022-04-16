import time

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget

from PyMediaCenter.mediaPlayer.controller import BottomControllers, AudioSubtitleSelector, CropRatioAspectSelector, TopControllers
from PyMediaCenter.mediaPlayer.layout import PlayerLayout
from PyMediaCenter.mediaPlayer.player import Player
from PyMediaCenter.medialibrary import MEDIA_TYPE_MOVIE, MEDIA_TYPE_TV


class MediaPlayer(QWidget):
    def __init__(self, model_manager, parent):
        QWidget.__init__(self, parent)
        self.setStyleSheet(MediaPlayerStylesheet)

        self.model_manager = model_manager
        self.model_manager.playlist_ready.connect(self.on_playlist_ready)


        self.player = Player(self)
        self.ctrl = BottomControllers(self)
        self.ctrl_top = TopControllers(self)
        self.ctrl_aspect = CropRatioAspectSelector(self)
        self.ctrl_audio = AudioSubtitleSelector(self)
        self.ctrl_aspect.setVisible(False)
        self.ctrl_audio.setVisible(False)

        self.player.position_changed.connect(self.ctrl.set_position)
        self.player.media_changed.connect(self.ctrl_top.update_media)

        self.ctrl.position_selected.connect(self.player.set_position)
        self.ctrl.button_play.clicked.connect(self.player.play)
        self.ctrl.button_language.clicked.connect(self.on_language)
        self.ctrl.button_aspect.clicked.connect(self.on_aspect)
        self.ctrl.button_next.clicked.connect(self.player.next)
        self.ctrl.button_previous.clicked.connect(self.player.previous)
        self.ctrl.button_fs.clicked.connect(self.window().full_screen)

        self.ctrl_top.button_close.clicked.connect(self.on_close)

        self.layout = PlayerLayout(self)
        self.layout.set_bottom_controller(self.ctrl)
        self.layout.set_player(self.player)
        self.layout.set_center_controller(self.ctrl_aspect, 0)
        self.layout.set_center_controller(self.ctrl_audio, 1)
        self.layout.set_top_controller(self.ctrl_top)
        self.setLayout(self.layout)

        self.last_move = time.time()

        self.timer_show = QTimer(self)
        self.timer_show.setInterval(1000)
        self.timer_show.timeout.connect(self.update_visible)
        self.timer_show.start()

        self.setMouseTracking(True)

    def on_close(self):
        self.hide_ctrl()
        self.player.stop()
        self.window().on_switch("library")

    def update_visible(self):
        if self.last_move + 3 < time.time():
            self.hide_ctrl()

    def hide_ctrl(self):
        if self.ctrl.isVisible():
            self.ctrl.setVisible(False)
        if self.ctrl_top.isVisible():
            self.ctrl_top.setVisible(False)
        if self.ctrl_aspect.isVisible():
            self.ctrl_aspect.setVisible(False)
        if self.ctrl_audio.isVisible():
            self.ctrl_audio.setVisible(False)
        if not self.ctrl.isVisible():
            self.setCursor(Qt.BlankCursor)

    def show_ctrl(self):
        if not self.ctrl.isVisible():
            self.ctrl.setVisible(True)
        if not self.ctrl_top.isVisible():
            self.ctrl_top.setVisible(True)
        self.unsetCursor()

    def on_aspect(self):
        if self.ctrl_aspect.isVisible():
            self.ctrl_aspect.setVisible(False)
            self.setFocus()
            return
        if self.ctrl_audio.isVisible():
            self.ctrl_audio.setVisible(False)
        self.ctrl_aspect.set_info(self.player.get_info_crop_ratio())
        self.ctrl_aspect.setVisible(True)
        self.ctrl_aspect.setFocus()

    def on_language(self):
        if self.ctrl_audio.isVisible():
            self.ctrl_audio.setVisible(False)
            self.setFocus()
            return
        if self.ctrl_aspect.isVisible():
            self.ctrl_aspect.setVisible(False)
        self.ctrl_audio.set_info(self.player.get_info_str_audio())
        self.ctrl_audio.setVisible(True)
        self.ctrl_audio.setFocus()

    def on_playlist_ready(self, playlist):
        self.window().on_switch("player")
        self.player.set_playlist(playlist)
        self.setFocus()

    def keyPressEvent(self, event):
        self.last_move = time.time()
        self.show_ctrl()
        if event.key() == Qt.Key_Escape:
            if self.ctrl_aspect.isVisible():
                self.ctrl_aspect.setVisible(False)
            elif self.ctrl_audio.isVisible():
                self.ctrl_audio.setVisible(False)
            else:
               self.on_close()
        elif event.key() == Qt.Key_N:
            self.player.next()
        elif event.key() == Qt.Key_P:
            self.player.next(-1)
        elif event.key() == Qt.Key_Space:
            self.player.play()
        elif event.key() == Qt.Key_A:
            self.on_language()
        elif event.key() == Qt.Key_C:
            self.on_aspect()
        elif event.key() == Qt.Key_Left:
            self.player.inc_time(-15)
        elif event.key() == Qt.Key_Right:
            self.player.inc_time(15)
        elif event.key() == Qt.Key_Down:
            self.player.inc_time(-120)
        elif event.key() == Qt.Key_Up:
            self.player.inc_time(+120)
        else:
            QWidget.keyPressEvent(self, event)

    def mouseMoveEvent(self, mouse_event):
        self.last_move = time.time()
        self.show_ctrl()
        QWidget.mouseMoveEvent(self, mouse_event)




MediaPlayerStylesheet = """
QLabel{
    color: white;
    font-size: 15pt;
}

BottomControllers, TopControllers, AudioSubtitleSelector, CropRatioAspectSelector{
     background-color: rgb(231, 62, 1);
     color: White
}

QSlider::groove:horizontal {
    background: white;
    height: 50px;
}

QSlider::handle:horizontal {
    background: black;
    width: 5px;
}

QSlider::add-page:horizontal {
    background: grey;
}

QSlider::sub-page:horizontal {
    background: white;
}

QGroupBox{
    background-color: rgb(231, 62, 1);
    color: white;
    font-size: 25pt;
    text-decoration: underline;
}

QRadioButton{
    color: white;
    font-size: 15pt;
}
    
"""