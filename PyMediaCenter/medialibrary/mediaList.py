from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QListView, QStyleOption, QStyle, QLineEdit, QComboBox, QVBoxLayout, QCheckBox, \
    QFrame, QSizePolicy, QHBoxLayout, QAbstractScrollArea

from PyMediaCenter.medialibrary.layout import MediaListLayout


class PosterListWidget(QFrame):
    doubleClicked = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent, library, line=0, wrapping=False):
        QFrame.__init__(self, parent)
        self.setStyleSheet("QScrollBar{height:0px}")
        self.library = library
        self.list = HListView(self, line, wrapping)
        box = QHBoxLayout(self)
        box.addWidget(self.list)
        self.setLayout(box)
        self.model = None
        self.list.doubleClicked.connect(self._on_click)

    def set_model(self, model):
        self.model = model
        self.list.setModel(model)

    def _on_click(self):
        selection = self.list.selectionModel()
        indexes = selection.selectedIndexes()
        if len(indexes) > 0:
            data = self.model.data(indexes[0])
            if data:
                self.on_click(data)
                self.doubleClicked.emit(data)

    def on_click(self, data):
        pass


class SeasonWidget(PosterListWidget):
    def on_click(self, data):
        self.library.new_tv_season_info(data["tv_id"], data["season_number"])


class MovieWidget(PosterListWidget):
    def on_click(self, data):
        self.library.new_movie_info(data["id"])


class TvWidget(PosterListWidget):
    def on_click(self, data):
        self.library.new_tv_info(data["id"])


class PersonWidget(PosterListWidget):
    def on_click(self, data):
        self.library.new_person_info(data["id"])


class HListView(QListView):
    def __init__(self, parent=None, line=1, wrapping=False):
        QListView.__init__(self, parent)
        self.poster_height = 375
        self.poster_width = 250
        if wrapping:
            self.poster_height = 450
            self.poster_width = 300
        self.line = line
        self.setViewMode(QListView.IconMode)
        self.setFlow(QListView.LeftToRight)
        if wrapping:
            self.setFlow(QListView.TopToBottom)
        self.setWrapping(wrapping)
        self.setLayoutMode(QListView.Batched)
        self.setIconSize(QSize(self.poster_width, self.poster_height))
        self.setGridSize(QSize(self.poster_width + 6, self.poster_height + (30*line) + 6))
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.sizeHintForRow(self.poster_height + (30*self.line) + 8)
        self.setUniformItemSizes(True)
        self.setBatchSize(30)
        self.setMinimumHeight(self.poster_height + (30*self.line) + 8)

    def wheelEvent(self, event):
        if event.angleDelta().x() == 0:
            event.ignore()
        else:
            return QListView.wheelEvent(self, event)


    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Return:
            selection = self.selectionModel()
            indexes = selection.selectedIndexes()
            self.doubleClicked.emit(indexes[0])
        else:
            QFrame.keyReleaseEvent(self, event)