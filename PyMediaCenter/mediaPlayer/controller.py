import datetime

from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QStyleOption, QStyle, QGroupBox, QVBoxLayout, QRadioButton, \
    QFrame

try:
    # new location for sip
    # https://www.riverbankcomputing.com/static/Docs/PyQt5/incompatibilities.html#pyqt-v5-11
    from PyQt5 import sip
except ImportError:
    import sip

from PyMediaCenter.medialibrary import MEDIA_TYPE_TV, MEDIA_TYPE_MOVIE
from PyMediaCenter.medialibrary.mediaView import convert_duration
from PyMediaCenter.widget import QIconButton, QJumpSlider


class BottomControllers(QFrame):
    position_selected = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)
        self.visible = True

        self.button_play = QIconButton(self, ":/rsc/play_white.png", ":/rsc/play_black.png", None)
        self.hbox.addWidget(self.button_play)

        self.button_previous = QIconButton(self, ":/rsc/previous_white.png", ":/rsc/previous_black.png", None)
        self.hbox.addWidget(self.button_previous)

        self.label_position_time = QLabel("--:--:--", self)
        self.hbox.addWidget(self.label_position_time)

        self.slider = QJumpSlider(Qt.Horizontal, self)
        self.slider.setMaximum(1000)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.sliderMoved.connect(self.on_slider_move)
        self.slider.valueChanged.connect(self.on_slider_changed)
        self.hbox.addWidget(self.slider)

        self.label_remaining_time = QLabel("--:--:--", self)
        self.hbox.addWidget(self.label_remaining_time)

        self.button_next = QIconButton(self, ":/rsc/next_white.png", ":/rsc/next_black.png", None)
        self.hbox.addWidget(self.button_next)

        self.button_language = QIconButton(self, ":/rsc/language_white.png", ":/rsc/language_black.png", None)
        self.hbox.addWidget(self.button_language)

        self.button_aspect = QIconButton(self, ":/rsc/aspect_white.png", ":/rsc/aspect_black.png", None)
        self.hbox.addWidget(self.button_aspect)

        self.button_fs = QIconButton(self, ":/rsc/fullscreen_white.png", ":/rsc/fullscreen_black.png", None)
        self.hbox.addWidget(self.button_fs)

        self.setFocusPolicy(Qt.NoFocus)

    def set_position(self, info):
        try:
            self.slider.valueChanged.disconnect(self.on_slider_changed)
        except TypeError:
            pass
        self.slider.setValue(info["position"] * 1000)
        self.slider.valueChanged.connect(self.on_slider_changed)
        self.set_timing(info["current_time"], info["total_time"])

    def on_slider_move(self, position):
        self.position_selected.emit(position/1000.0)

    def on_slider_changed(self):
        self.position_selected.emit(self.slider.value() / 1000.0)

    def set_timing(self, timing, total_time):
        self.label_position_time.setText(convert_duration(timing))
        self.label_remaining_time.setText(convert_duration(total_time-timing))


class TopControllers(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self, parent)
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)
        self.button_menu = QIconButton(self, ":/rsc/menu_white.png", ":/rsc/menu_black.png", None)
        self.hbox.addWidget(self.button_menu)
        self.label_name = QLabel("----", self)
        self.hbox.addWidget(self.label_name)
        self.hbox.addStretch()
        self.label_time = QLabel("--:--", self)
        self.hbox.addWidget(self.label_time)
        self.button_close = QIconButton(self, ":/rsc/close_white.png", ":/rsc/close_black.png", None)
        self.hbox.addWidget(self.button_close)

        self.timer = QTimer(self)
        self.timer.setInterval(10*1000)
        self.timer.timeout.connect(self.update_time)
        self.timer.start()

        self.update_time()

    def update_media(self, media):
        self.label_name.setText(media)

    def update_time(self):
        time = datetime.datetime.now()
        self.label_time.setText(str(time.hour)+":"+str(time.minute))


class CropRatioAspectSelector(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self, parent)
        self.player = parent.player
        self.list = ["Default", "16:9", "16:10", "4:3", "1:1", "11:8", "14:9", "21:9", "2.2:1"]

    def set_info(self, info):
        main_box = QVBoxLayout()
        group_box_device = QGroupBox("Proportion: ")
        group_box_device_layout = QVBoxLayout()
        for i in range(0, len(self.list)):
            radio = QRadioButton(self.list[i])
            if info["ratio"] == self.list[i] or (self.list[i] == "Default" and info["ratio"] is None):
                radio.setChecked(True)
            radio.toggled.connect(lambda c, nfo=self.list[i]: self.on_ratio(c, nfo))
            group_box_device_layout.addWidget(radio)
        group_box_device_layout.addStretch()
        group_box_device.setLayout(group_box_device_layout)
        main_box.addWidget(group_box_device)

        group_box_device = QGroupBox("Rogner :")
        group_box_device_layout = QVBoxLayout()
        for i in range(0, len(self.list)):
            radio = QRadioButton(self.list[i])
            if info["crop"] == self.list[i] or (self.list[i] == "Default" and info["crop"] is None):
                radio.setChecked(True)
            radio.toggled.connect(lambda c, nfo=self.list[i]: self.on_crop(c, nfo))
            group_box_device_layout.addWidget(radio)
        group_box_device_layout.addStretch()
        group_box_device.setLayout(group_box_device_layout)
        main_box.addWidget(group_box_device)

        if self.layout():
            sip.delete(self.layout())
        self.setLayout(main_box)

    def on_ratio(self, check, ratio):
        if check:
            if ratio == "Default":
                ratio = None
            self.player.set_ratio(ratio)

    def on_crop(self, check, crop):
        if check:
            if crop == "Default":
                crop = None
            self.player.set_crop(crop)


class AudioSubtitleSelector(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self, parent)
        self.player = parent.player

    def set_info(self, info):
        main_box = QVBoxLayout()
        if len(info["Devices"]) > 1:
            group_box_device = QGroupBox("Selection sortie audio")
            group_box_device_layout = QVBoxLayout()
            for i in range(0, len(info["Devices"])):
                radio = QRadioButton(info["Devices"][i].decode())
                radio.toggled.connect(lambda c, nfo=info["Devices"][i]: self.on_device(c, nfo))
                group_box_device_layout.addWidget(radio)
            group_box_device_layout.addStretch()
            group_box_device.setLayout(group_box_device_layout)
            main_box.addWidget(group_box_device)

        if len(info["Audios"]) > 0:
            group_box_device = QGroupBox("Selection audio")
            group_box_device_layout = QVBoxLayout()
            for i in range(0, len(info["Audios"])):
                radio = QRadioButton(info["Audios"][i][1].decode())
                if info["Audios-selected"] == info["Audios"][i][0]:
                    radio.setChecked(True)
                radio.toggled.connect(lambda c, nfo=info["Audios"][i][0]: self.on_audio(c, nfo))
                group_box_device_layout.addWidget(radio)
            group_box_device_layout.addStretch()
            group_box_device.setLayout(group_box_device_layout)
            main_box.addWidget(group_box_device)

        if len(info["Subtitles"]) > 0:
            group_box_device = QGroupBox("Selection sous-titre")
            group_box_device_layout = QVBoxLayout()
            for i in range(0, len(info["Subtitles"])):
                radio = QRadioButton(info["Subtitles"][i][1].decode())
                if info["Subtitles-selected"] == info["Subtitles"][i][0]:
                    radio.setChecked(True)
                radio.toggled.connect(lambda c, nfo=info["Subtitles"][i][0]: self.on_subtitle(c, nfo))
                group_box_device_layout.addWidget(radio)
            group_box_device_layout.addStretch()
            group_box_device.setLayout(group_box_device_layout)
            main_box.addWidget(group_box_device)

        main_box.addStretch()

        if self.layout() is not None:
            sip.delete(self.layout())
        for child in self.children():
            sip.delete(child)
        self.setLayout(main_box)

    def on_device(self, check, value):
        if check:
            self.player.set_audio_device(value)

    def on_subtitle(self, check, value):
        if check:
            self.player.set_subtitle(value)

    def on_audio(self, check, value):
        if check:
            self.player.set_audio(value)


