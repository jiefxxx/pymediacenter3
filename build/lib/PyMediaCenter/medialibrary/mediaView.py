import math
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QVariant, QBasicTimer
from PyQt5.QtGui import QPainter, QPixmap, QPalette, QBrush, QGuiApplication
from PyQt5.QtWidgets import QWidget, QStyleOption, QStyle, QLabel, QVBoxLayout, QHBoxLayout, QApplication, QScrollArea, \
    QGridLayout, QListView, QHeaderView, QAbstractItemView, QTableView, QFrame


class Link(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.timer = QBasicTimer()

    def mouseReleaseEvent(self, ev):
        if self.timer.isActive():
            self.timer.stop()
            self.on_click()
        else:
            self.timer.start(300, self)

    def timerEvent(self, ev):
        self.timer.stop()

    def on_click(self):
        pass

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.on_click()
        else:
            QLabel.keyReleaseEvent(self, event)


class LinkPerson(Link):
    def __init__(self, parent, library, person_id, text):
        Link.__init__(self, parent)
        self.library = library
        self.id = person_id
        self.setText(text)

    def on_click(self):
        self.library.new_person_info(self.id)


class LinkGenre(Link):
    def __init__(self, parent, library, genre_name):
        Link.__init__(self, parent)
        self.library = library
        self.genre_name = genre_name
        self.setText(genre_name)

    def on_click(self):
        print("yeah")


class LinkTrailer(Link):
    def __init__(self, parent, library, youtube_id, text):
        Link.__init__(self, parent)
        self.library = library
        self.id = youtube_id
        self.setText(text)

    def on_click(self):
        print("yeah")


class TrailerView(QFrame):
    def __init__(self, parent, library):
        QFrame.__init__(self, parent)
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.library = library

    def set_trailer(self, trailers):
        for row, trailer in enumerate(trailers):
            title = LinkTrailer(self, self.library, trailer["youtube_id"], trailer["name"])
            title.setObjectName("Link")
            title.setWordWrap(True)
            icon = QLabel(self)
            pixmap = QPixmap(":/rsc/youtube.png")
            pixmap = pixmap.scaledToHeight(title.height(), mode=Qt.SmoothTransformation)
            icon.setPixmap(pixmap)

            self.grid_layout.addWidget(icon, row, 0, 1, 1)
            self.grid_layout.addWidget(title, row, 1, 1, 11)


class SeeView(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.setObjectName("See")

    def set_see(self, watched):
        if watched:
            pixmap = QPixmap(":/rsc/see-full.png")
        else:
            pixmap = QPixmap(":/rsc/see-empty.png")
        pixmap = pixmap.scaledToHeight(self.height(), mode=Qt.SmoothTransformation)
        self.setPixmap(pixmap)


class PosterView(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setObjectName("Poster")
        self.setMargin(10)
        self.timer = QBasicTimer()

    def mousePressEvent(self, ev):
        pass

    def mouseReleaseEvent(self, ev):
        if self.timer.isActive():
            self.timer.stop()
            self.clicked.emit()
        else:
            self.timer.start(300, self)

    def timerEvent(self, ev):
        self.timer.stop()

    def set_pixmap(self, pixmap):
        if pixmap is None:
            pixmap = QPixmap(":/rsc/404.jpg")
        rect = QApplication.desktop().screenGeometry()
        pixmap = pixmap.scaledToWidth(rect.width()/6, mode=Qt.SmoothTransformation)
        self.setPixmap(pixmap)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.clicked.emit()
        elif event.key() == Qt.Key_Down:
            self.focusNextChild()
        elif event.key() == Qt.Key_Up:
            self.focusPreviousChild()
        else:
            QLabel.keyReleaseEvent(self, event)


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
