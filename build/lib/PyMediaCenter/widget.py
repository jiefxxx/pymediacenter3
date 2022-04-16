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


class QSelectorIcon(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent, normal, clicked, selected, size):
        QLabel.__init__(self, parent=parent)
        self._selected = False
        self.n_pixmap = QPixmap(normal)
        self.p_pixmap = QPixmap(clicked)
        self.s_pixmap = QPixmap(selected)
        self._current_pixmap = self.n_pixmap
        self.size = size

    def _resize(self, pixmap):
        if self.size:
            return pixmap.scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            return pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def set_pixmap(self, pixmap):
        self._current_pixmap = pixmap
        self.setPixmap(self._resize(self._current_pixmap))

    def set_selected(self, b):
        self._selected = b
        if b:
            self.set_pixmap(self.s_pixmap)
        else:
            self.set_pixmap(self.n_pixmap)

    def selected(self):
        return self._selected

    def resizeEvent(self, event):
        self.setPixmap(self._resize(self._current_pixmap))

    def mousePressEvent(self, ev):
        self.set_pixmap(self.p_pixmap)

    def mouseReleaseEvent(self, ev):
        self.clicked.emit()
        if self._selected:
            self.set_pixmap(self.s_pixmap)
        else:
            self.set_pixmap(self.n_pixmap)


class QIconButton(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent, normal, clicked, size):
        QLabel.__init__(self, parent)
        self.n_pixmap = QPixmap(normal)
        self.p_pixmap = QPixmap(clicked)
        self._current_pixmap = self.n_pixmap
        self.size = size

    def _resize(self, pixmap):
        if self.size:
            return pixmap.scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            return pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def set_pixmap(self, pixmap):
        try:
            self._current_pixmap = pixmap
            self.setPixmap(self._resize(self._current_pixmap))
        except RuntimeError:
            pass

    def resizeEvent(self, event):
        self.setPixmap(self._resize(self._current_pixmap))

    def mousePressEvent(self, ev):
        self.set_pixmap(self.p_pixmap)

    def mouseReleaseEvent(self, ev):
        self.clicked.emit()
        self.set_pixmap(self.n_pixmap)


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