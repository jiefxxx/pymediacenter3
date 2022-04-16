import math
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QVariant
from PyQt5.QtGui import QPainter, QPixmap, QPalette, QBrush, QGuiApplication
from PyQt5.QtWidgets import QWidget, QStyleOption, QStyle, QLabel, QVBoxLayout, QHBoxLayout, QApplication, QScrollArea, \
    QGridLayout, QListView, QHeaderView, QAbstractItemView, QTableView, QFrame


class MediaView(QFrame):

    def __init__(self, parent, data):
        QFrame.__init__(self, parent)
        self.new_playlist = parent.new_playlist
        self.setAutoFillBackground(True)
        self.data = data
        self.poster = QLabel(self)

        rect = QApplication.desktop().screenGeometry()

        self.setObjectName("mediaView")

        self.pixmap_poster = data["Poster"].scaledToWidth(rect.width()/5, mode=Qt.SmoothTransformation)
        self.pixmap_background = data["Backdrop"]
        self.poster.setPixmap(self.pixmap_poster)

        self.title = QLabel()
        self.title.setObjectName("Title")
        self.title.setText(data["Title"])
        self.title.setWordWrap(True)

        self.original_title = QLabel()
        self.original_title.setObjectName("OriginalTitle")
        self.original_title.setText(data["OriginalTitle"])
        self.original_title.setWordWrap(True)

        self.release = QLabel()
        self.release.setText(data["ReleaseDate"])

        self.vote = QLabel()
        self.vote.setText(str(round(data["VoteAverage"], 1)))

        self.genres_label = QLabel()
        try:
            self.genres_label.setText(", ".join(data["Genres"]))
        except TypeError:
            pass
        self.genres_label.setWordWrap(True)

        self.overview = QLabel()
        self.overview.setText(data["Overview"])
        self.overview.setWordWrap(True)

        self.movie_vbox = QVBoxLayout()
        self.movie_vbox.addWidget(self.title)
        self.movie_vbox.addWidget(self.original_title)
        self.movie_vbox.addWidget(self.release)
        self.movie_vbox.addWidget(self.vote)
        self.movie_vbox.addWidget(self.genres_label)
        self.movie_vbox.addWidget(self.overview, stretch=True)

        hbox = QHBoxLayout()
        hbox.addWidget(self.poster)
        hbox.addLayout(self.movie_vbox, stretch=True)

        self.main_box = QVBoxLayout()
        self.main_box.addLayout(hbox)

        widget = QFrame()
        widget.setLayout(self.main_box)
        self.scroll_widget = QScrollArea()
        self.scroll_widget.setWidgetResizable(True)
        self.scroll_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_widget.setWidget(widget)

        self.scroll_box = QVBoxLayout()
        self.scroll_box.addWidget(self.scroll_widget)
        self.setLayout(self.scroll_box)

        self.items = []
        self.current = 0

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        if self.pixmap_background:
            p.drawPixmap(self.rect(), self.pixmap_background)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def select_item(self, nbr):
        if not 0 <= nbr < len(self.items):
            return None
        self.items[self.current].unselected()
        self.items[nbr].selected()
        self.current = nbr
        self.scroll_widget.ensureWidgetVisible(self.items[nbr])
        return self.items[nbr]

    def keyPressEvent(self, event):
        if self.items[self.current].active:
            QFrame.keyPressEvent(self, event)
            return

        if event.key() == Qt.Key_Return:
            self.items[self.current].pressed()
        elif event.key() == Qt.Key_Down:
            pass
        elif event.key() == Qt.Key_Up:
            pass
        else:
            QFrame.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        if self.items[self.current].active:
            QFrame.keyReleaseEvent(self, event)
            return
        if event.key() == Qt.Key_Return:
            self.items[self.current].released()
        elif event.key() == Qt.Key_Down:
            self.select_item(self.current + 1)
        elif event.key() == Qt.Key_Up:
            self.select_item(self.current - 1)
        else:
            QFrame.keyReleaseEvent(self, event)


class MovieItemView(QFrame):
    def __init__(self, video, parent):
        QFrame.__init__(self, parent)
        self.new_playlist = parent.new_playlist
        self.main_box = QHBoxLayout(self)
        self.videoID = video["VideoID"]
        if video["Timestamp"]:
            self.main_box.addWidget(QLabel("V"))
        else:
            self.main_box.addWidget(QLabel("O"))
        self.main_box.addWidget(QLabel(video["Path"].split("/")[-1]))
        self.main_box.addWidget(QLabel(convert_size(video["Size"])))
        self.main_box.addWidget(QLabel(convert_duration(video["Duration"])))
        try:
            self.main_box.addWidget(QLabel("Languages :" + ", ".join(video["Audios"])))
        except TypeError:
            pass
        try:
            self.main_box.addWidget(QLabel("Subtitles :" + ", ".join(video["Subtitles"])))
        except TypeError:
            pass
        self.main_box.addStretch()
        self.setLayout(self.main_box)
        self.setObjectName("RowItemBase")
        self.prev = self.objectName()
        self.active = False

    def pressed(self):
        self.prev = self.objectName()
        self.setObjectName("RowItemClicked")
        self.setStyleSheet("\*")

    def released(self):
        self.new_playlist.emit([self.videoID])
        self.setObjectName(self.prev)
        self.setStyleSheet("\*")

    def selected(self):
        self.setObjectName("RowItemSelected")
        self.setStyleSheet("\*")

    def unselected(self):
        self.setObjectName("RowItemBase")
        self.setStyleSheet("\*")

    def mousePressEvent(self, ev):
        self.pressed()

    def mouseReleaseEvent(self, ev):
        self.released()


class TvItemDescription(QFrame):
    def __init__(self, season_number, season, parent):
        QFrame.__init__(self, parent)
        self.new_playlist = parent.new_playlist
        self.scroll_widget = parent.scroll_widget
        self.season = season
        self.main_box = QVBoxLayout(self)
        self.header = SeasonHeader(season_number, self)
        self.main_box.addWidget(self.header)
        self.episodes = SeasonListView(season, self)
        self.episodes.setVisible(False)
        self.episodes.doubleClicked.connect(self.on_selection_validate)
        self.main_box.addWidget(self.episodes)
        self.setLayout(self.main_box)
        self.active = False

    def on_selection_validate(self, ignore=None):
        ret = []
        row = self.episodes.currentIndex().row()
        proxy = self.episodes.model()
        model = proxy.sourceModel()
        while True:
            proxy_index = proxy.index(row, 0)
            index = proxy.mapToSource(proxy_index)
            data = model.data(index)
            if type(data) is QVariant:
                break
            ret.append(data["VideoID"])
            row += 1
        self.new_playlist.emit(ret)

    def pressed(self):
        self.header.pressed()

    def released(self):
        self.episodes.setVisible(not self.episodes.isVisible())
        self.active = not self.active
        self.header.released()
        self.episodes.setFocus()
        self.episodes.selectRow(0)

    def mousePressEvent(self, ev):
        self.pressed()

    def mouseReleaseEvent(self, ev):
        self.released()

    def selected(self):
        self.header.selected()

    def unselected(self):
        self.header.unselected()


class MovieView(MediaView):
    def __init__(self, parent, data):
        MediaView.__init__(self, parent, data)
        self.items = []
        for video in data["Videos"]:
            item = MovieItemView(video, self)
            self.main_box.addWidget(item)
            self.items.append(item)
        self.main_box.addStretch()
        self.select_item(self.current)


class TvView(MediaView):
    def __init__(self, parent, data):
        MediaView.__init__(self, parent, data)
        self.items = []
        l = list(data["Seasons"].keys())
        l.sort()
        for season_number in l:
            item = TvItemDescription(season_number, data["Seasons"][season_number], self)
            self.main_box.addWidget(item)
            self.items.append(item)
        self.main_box.addStretch()
        self.select_item(self.current)


class SeasonListView(QTableView):
    def __init__(self, season, parent):
        QTableView.__init__(self, parent)
        self.saison = parent
        self.setModel(season)
        self.setSortingEnabled(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalHeader().setVisible(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setWordWrap(True)
        self.setTextElideMode(Qt.ElideNone)
        self.selection = self.selectionModel().selectionChanged.connect(self.on_selection)

        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeColumnToContents(2)

        self.setFixedHeight(self.get_height())

    def on_selection(self, item_selected):
        index = self.selectionModel().selectedRows()[0]
        pos = self.rowViewportPosition(index.row())
        point = self.parent().mapToParent(self.mapToParent(QPoint(0, pos)))
        self.parent().scroll_widget.ensureVisible(point.x(), point.y())


    def get_height(self):
        h = 4
        for i in range(self.model().rowCount()):
            self.resizeRowToContents(i)
            h += self.rowHeight(i)
        return h

    def resizeEvent(self, event):
        prev_columns = 0
        for i in range(0, self.model().columnCount()-1):
            prev_columns += self.columnWidth(i)
        self.setColumnWidth(self.model().columnCount()-1, self.width()-prev_columns-4)
        self.setFixedHeight(self.get_height())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.saison.pressed()
        elif event.key() == Qt.Key_Return:
            pass
        else:
            QTableView.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.saison.setFocus()
            self.saison.released()
        elif event.key() == Qt.Key_Return:
            self.saison.on_selection_validate()
        else:
            QTableView.keyReleaseEvent(self, event)


class SeasonHeader(QFrame):
    def __init__(self, season_number, parent):
        QFrame.__init__(self, parent)
        self.main_box = QVBoxLayout(self)
        self.label = QLabel("Saison "+str(season_number))
        self.main_box.addWidget(self.label, stretch=True)
        self.setLayout(self.main_box)
        self.setObjectName("RowItemBase")
        self.prev = self.objectName()

    def pressed(self):
        self.prev = self.objectName()
        self.setObjectName("RowItemClicked")
        self.setStyleSheet("\*")

    def released(self):
        self.setObjectName(self.prev)
        self.setStyleSheet("\*")

    def selected(self):
        self.setObjectName("RowItemSelected")
        self.setStyleSheet("\*")

    def unselected(self):
        self.setObjectName("RowItemBase")
        self.setStyleSheet("\*")



def convert_size(size_bytes):
    if size_bytes == 0 or size_bytes is None:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def convert_duration(millis):
    seconds = int(millis/1000)
    return time.strftime('%H:%M:%S', time.gmtime(seconds))
