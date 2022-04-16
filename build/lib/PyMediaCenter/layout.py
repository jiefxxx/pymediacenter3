from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QLayout


class BaseLayout(QLayout):
    def __init__(self, parent=None):
        QLayout.__init__(self, parent)
        self.list = []

    def count(self):
        return len(self.list)

    def itemAt(self, i):
        if 0 <= i < len(self.list):
            return self.list[i]

    def takeAt(self, i):
        ret = self.list[i]
        self.list.remove(ret)
        return ret

    def addItem(self, item):
        self.list.append(item)


class CentralLayout(BaseLayout):
    def __init__(self, parent=None):
        BaseLayout.__init__(self, parent)
        self.item = None

    def set_widget(self, widget):
        self.list = []
        self.addWidget(widget)
        self.item = widget

    def sizeHint(self):
        return QSize(640, 480)

    def setGeometry(self, top_rec):
        if self.item:
            self.item.setGeometry(0, 0, top_rec.width(), top_rec.height())

