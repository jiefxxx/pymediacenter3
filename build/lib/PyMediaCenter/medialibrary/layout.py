from PyQt5.QtCore import QSize

from PyMediaCenter.layout import BaseLayout

class MediaLibraryLayout(BaseLayout):
    def __init__(self, media_list, nav, process_label, parent=None):
        BaseLayout.__init__(self, parent)
        self.media_list = media_list
        self.nav = nav
        self.process_label = process_label
        self.addWidget(self.media_list)
        self.addWidget(self.nav)
        self.addWidget(self.process_label)

        self.test = True

    def set_media_list(self, media_list):
        self.media_list = media_list
        self.addWidget(self.media_list)

    def sizeHint(self):
        return QSize(640, 480)

    def setGeometry(self, top_rec):
        nav_width = top_rec.width() * 1 / 15
        if nav_width < 100:
            nav_width = 100
        self.process_label.setGeometry(((top_rec.width() - nav_width) / 2) - 64 + nav_width,
                                       (top_rec.height()/2)-64, 128, 128)
        self.nav.setGeometry(0, 0, nav_width, top_rec.height())
        self.media_list.setGeometry(nav_width, 0, top_rec.width()-nav_width, top_rec.height())
        self.media_list.stackUnder(self.process_label)


class MediaListLayout(BaseLayout):
    def __init__(self, poster_list, search_header, ctrl_display, parent=None):
        BaseLayout.__init__(self, parent)
        self.poster_list = poster_list
        self.search = search_header
        self.ctrl_display = ctrl_display
        self.addWidget(self.poster_list)
        self.addWidget(self.search)
        self.addWidget(self.ctrl_display)

    def sizeHint(self):
        return QSize(640, 480)

    def setGeometry(self, top_rec):
        self.poster_list.setGeometry(0, 0, top_rec.width(), top_rec.height())
        self.search.setGeometry(0, 0, top_rec.width()/3, top_rec.height()/15)
        if self.ctrl_display is not None:
            size = self.ctrl_display.sizeHint()
            self.ctrl_display.setGeometry((top_rec.width()-size.width())/2,
                                          (top_rec.height()-size.height())/2,
                                          size.width(),
                                          size.height())
            self.poster_list.stackUnder(self.ctrl_display)
        self.poster_list.stackUnder(self.search)
