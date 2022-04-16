from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QListView, QStyleOption, QStyle, QLineEdit, QComboBox, QVBoxLayout, QCheckBox, \
    QFrame

from PyMediaCenter.medialibrary.layout import MediaListLayout


class SearchLine(QLineEdit):
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.setVisible(False)
        else:
            QLineEdit.keyPressEvent(self, event)


class CtrlListWidget(QFrame):
    def __init__(self, parent, model):
        QFrame.__init__(self, parent)
        self.model = model
        self.main_box = QVBoxLayout(self)
        try:
            keys = self.model.get_sort_keys()
        except AttributeError:
            return
        if keys is not None:
            self.sort_combo_widget = QComboBox(self)
            for view, data in keys:
                self.sort_combo_widget.addItem(view, userData=data)

            self.main_box.addWidget(self.sort_combo_widget)
            self.sort_combo_widget.currentIndexChanged.connect(self.on_sort_combo)

            self.sort_revers_check = QCheckBox("Inversé la sélection", self)
            self.sort_revers_check.stateChanged.connect(self.on_sort_revers)
            self.main_box.addWidget(self.sort_revers_check)

    def on_sort_combo(self, index):
        self.model.set_sort_key(self.sort_combo_widget.itemData(index))
        self.model.do_sort()

    def on_sort_revers(self, state):
        reverse = False
        if state == Qt.Checked:
            reverse = True
        self.model.set_reverse(reverse)
        self.model.do_sort()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.setVisible(False)
        else:
            QFrame.keyPressEvent(self, event)


class ListWidget(QFrame):
    def __init__(self, parent, model):
        QFrame.__init__(self, parent)
        self.setStyleSheet("QScrollBar{height:0px}")
        self.library = parent
        self.poster = PosterListView(self)
        self.model = model
        self.poster.setModel(self.model)
        self.poster.setCurrentIndex(self.model.index(0, 0))

        self.search = SearchLine(self)
        self.search.setVisible(False)
        self.search.textEdited.connect(self.on_search)

        self.ctrl_display = CtrlListWidget(self, self.model)
        self.ctrl_display.setVisible(False)

        self.setLayout(MediaListLayout(self.poster, self.search, self.ctrl_display, self))

    def on_search(self, text):
        if self.model.set_search_string:
            self.model.set_search_string(text)

    def set_search(self, text):
        self.search.setText(text)
        self.search.setFocus()
        self.search.setVisible(True)
        self.on_search(text)

    def set_control(self):
        self.ctrl_display.setFocus()
        self.ctrl_display.setVisible(True)

    def get_selected_data(self):
        selection = self.poster.selectionModel()
        indexes = selection.selectedIndexes()
        if len(indexes) == 0:
            return None
        return self.model.data(indexes[0])

    def setFocus(self):
        self.poster.setFocus()


class MediaList(ListWidget):
    def __init__(self, parent, model):
        ListWidget.__init__(self, parent, model)
        self.poster.selection_validated.connect(self.on_media_selected)

    def on_media_selected(self):
        data = self.get_selected_data()
        if data:
            self.library.new_media_view(data["ID"], data["MediaType"])


class GenreList(ListWidget):
    def __init__(self, parent, model):
        ListWidget.__init__(self, parent, model)
        self.poster.selection_validated.connect(self.on_genre_selected)

    def on_genre_selected(self):
        data = self.get_selected_data()
        if data:
            self.library.new_media_genre_list(data["Name"])


class PosterListView(QListView):
    selection_validated = pyqtSignal()

    def __init__(self, parent=None, callback=None):
        QListView.__init__(self, parent)

        self.poster_height = 230
        self.poster_width = 154

        self.setFlow(QListView.LeftToRight)
        self.setResizeMode(QListView.Adjust)
        self.setWrapping(True)
        self.setViewMode(QListView.IconMode)
        self.setLayoutMode(QListView.Batched)

        self.doubleClicked.connect(self._on_double_clicked)

    def _on_double_clicked(self):
        self.selection_validated.emit()

    def setGeometry(self, x, y, w, h):
        n = int((w - 1)/180)
        if n > 6:
            n = 6
        if n > 0:
            w_ = float((w - 1)/ n)
            h_ = w_ * 234 / 158
            self.setGridSize(QSize(w_, h_))
            self.setIconSize(QSize(w_ - 4, h_ - 4))
        QListView.setGeometry(self, x, y, w, h)

    def keyPressEvent(self, event):
        text = event.text()
        if event.key() == Qt.Key_Return:
            self.selection_validated.emit()
        elif event.key() == Qt.Key_Backspace:
            self.parent().set_search("")
            self.parent().on_search("")
        elif event.key() == Qt.Key_Control:
            self.parent().set_control()
        elif text.isalpha() or text.isdigit():
            self.parent().set_search(text)
        else:
            QListView.keyPressEvent(self, event)