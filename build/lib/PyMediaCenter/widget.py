from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import QSlider, QLabel, QStyle, QDialog, QDialogButtonBox, QVBoxLayout


class WidgetSpinner(QLabel):
    def __init__(self, w, h, parent):
        QLabel.__init__(self, parent)
        self.movie = QMovie("/home/jief/workspace/python-mediaMananger/rsc/loading.gif")
        self.movie.setScaledSize(QSize(w, h))
        self.setMovie(self.movie)
        self.setVisible(False)

    def start(self):
        self.movie.start()
        self.setVisible(True)

    def stop(self):
        self.setVisible(False)
        self.movie.stop()


class QIconButton(QLabel):
    clicked = pyqtSignal()

    def __init__(self, path, parent=None, width=None, height=None):
        QLabel.__init__(self, parent)
        self.n_pixmap = QPixmap(path[0])
        self.p_pixmap = QPixmap(path[1])
        self._width = width
        self._height = height

    def _resize(self, pixmap):
        width = self._width
        height = self._height
        if width is None:
            width = self.width()
        if height is None:
            height = self.height()
        return pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def resizeEvent(self, event):
        self.setPixmap(self._resize(self.n_pixmap))

    def mousePressEvent(self, ev):
        self.setPixmap(self._resize(self.p_pixmap))

    def mouseReleaseEvent(self, ev):
        self.clicked.emit()
        self.setPixmap(self._resize(self.n_pixmap))



class QJumpSlider(QSlider):

    def mousePressEvent(self, ev):
        """ Jump to click position """
        self.setValue(QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), ev.x(), self.width()))

    def mouseMoveEvent(self, ev):
        """ Jump to pointer position while moving """
        self.setValue(QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), ev.x(), self.width()))

class ErrorDialog(QDialog):

    def __init__(self, message, *args, **kwargs):
        super(ErrorDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle("Fatal ERROR")

        buttons = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Erreur fatal: le programme doit être arreté! :"))
        self.layout.addWidget(QLabel(message))
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)