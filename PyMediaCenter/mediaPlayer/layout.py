try:
    # new location for sip
    # https://www.riverbankcomputing.com/static/Docs/PyQt5/incompatibilities.html#pyqt-v5-11
    from PyQt5 import sip
except ImportError:
    import sip

from PyQt5.QtCore import QSize, QRect

from PyMediaCenter.layout import BaseLayout


class PlayerLayout(BaseLayout):
    def __init__(self, parent=None):
        BaseLayout.__init__(self, parent)
        self.player = None
        self.bottom_controller = None
        self.top_controller = None
        self.center_controller = [None, None, None]

    def reset_widget(self, old, new):
        if old is not None:
            self.removeWidget(old)
            sip.delete(old)
        if new is not None:
            self.addWidget(new)
        return new

    def set_player(self, player):
        self.player = self.reset_widget(self.player, player)

    def set_top_controller(self, top_controller):
        self.top_controller = self.reset_widget(self.top_controller, top_controller)

    def set_bottom_controller(self, bottom_controller):
        self.bottom_controller = self.reset_widget(self.bottom_controller, bottom_controller)

    def set_center_controller(self, center_controller, i):
        self.center_controller[i] = self.reset_widget(self.center_controller[i], center_controller)

    def sizeHint(self):
        return QSize(640, 480)

    def setGeometry(self, top_rec):
        controllers_height = int(top_rec.height() / 100 * 7)
        if controllers_height < 40:
            controllers_height = 40

        controllers_width = int(top_rec.width() / 3)

        if self.player:
            self.player.setGeometry(0, 0, top_rec.width(), top_rec.height())

        if self.bottom_controller:
            self.bottom_controller.setGeometry(0, int(top_rec.height()-controllers_height),
                                               top_rec.width(), int(controllers_height))

        if self.top_controller:
            self.top_controller.setGeometry(0, 0, top_rec.width(), controllers_height)

        maxh = top_rec.height() - 2*(controllers_height + 10)
        for i in range(0, len(self.center_controller)):
            if self.center_controller[i]:
                hint = self.center_controller[i].sizeHint()
                h = hint.height()
                w = hint.width()
                if h > maxh:
                    h = maxh
                if w > controllers_width:
                    w = controllers_width
                x = top_rec.width() - w - 10
                y = controllers_height + 10 + maxh - h
                self.center_controller[i].setGeometry(QRect(x, y, w, h))
