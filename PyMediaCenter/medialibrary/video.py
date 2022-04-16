from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QTableView, QAbstractItemView, QHeaderView

from PyMediaCenter.medialibrary.model import VideoModel


class VideoChooser(QFrame):
    video_info = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, library):
        QFrame.__init__(self, library)
        self.library = library
        self.media_type = None

        main_box = QVBoxLayout()
        self.setLayout(main_box)

        self.table = QTableView(self)
        self.table.setObjectName("VideoTable")

        self.model = VideoModel([])

        self.table.setModel(self.model)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(header.logicalIndexAt(0), QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.verticalHeader().hide()

        main_box.addWidget(self.table)

        self.setVisible(False)

        self.table.doubleClicked.connect(self._on_selection)

        self.video_info.connect(self.on_video_info)

    def _on_selection(self):
        selection = self.table.selectionModel()
        indexes = selection.selectedIndexes()
        if len(indexes) > 0:
            data = self.table.model().data(indexes[0])
            if data and self.media_type == "movie":
                self.library.model_manager.play_movie(data)
            elif data and self.media_type == "tv":
                self.library.model_manager.play_episode(data)

    def sizeHint(self):
        return QSize(1400, 300)

    def set_media_id(self, media_type, media_id):
        self.media_type = media_type
        self.library.model_manager.get_videos(media_type, media_id, self.video_info)

    def on_video_info(self, title, l):
        if len(l) == 1:
            if self.media_type == "movie":
                self.library.model_manager.play_movie(l[0])
            elif self.media_type == "tv":
                self.library.model_manager.play_episode(l[0])
            return

        self.model.reset_data(l)
        self.setVisible(True)
        self.repaint()

        