from PyQt5.QtCore import QSize

from PyMediaCenter.layout import BaseLayout


class TopMenuLayout(BaseLayout):
    def __init__(self, poster, menu):
        BaseLayout.__init__(self)
        self.poster = poster
        self.menu = menu

        self.addWidget(self.poster)
        self.addWidget(self.menu)

    def setGeometry(self, top_rec):

        self.poster.setGeometry(top_rec.x(), top_rec.y(), top_rec.width(), top_rec.height())
        size = self.menu.sizeHint()
        print(size.width(), size.height())
        self.menu.setGeometry(0, (top_rec.height() / 2) - (size.height() / 2), top_rec.width(), size.height())
        self.poster.stackUnder(self.menu)

    def sizeHint(self):
        return QSize(640, 480)


class MediaLibraryLayout(BaseLayout):
    def __init__(self, media_list, process_label, video_chooser, parent=None):
        BaseLayout.__init__(self, parent)
        self.media_list = media_list
        self.process_label = process_label
        self.video_chooser = video_chooser
        self.addWidget(self.media_list)
        self.addWidget(self.process_label)

        self.test = True

    def set_media_list(self, media_list):
        self.media_list = media_list
        self.addWidget(self.media_list)

    def sizeHint(self):
        return QSize(640, 480)

    def setGeometry(self, top_rec):
        self.process_label.setGeometry((top_rec.width()/2)-64, (top_rec.height()/2)-64, 128, 128)

        size = self.video_chooser.sizeHint()
        self.video_chooser.setGeometry(0, (top_rec.height()/2)-(size.height()/2), top_rec.width(), size.height())

        self.media_list.setGeometry(0, 0, top_rec.width(), top_rec.height())

        self.media_list.stackUnder(self.video_chooser)
        self.video_chooser.stackUnder(self.process_label)


class SimpleListLayout(BaseLayout):
    def __init__(self, parent, poster_list):
        BaseLayout.__init__(self, parent)
        self.poster_list = poster_list

    def sizeHint(self):
        return QSize(640, 480)

    def setGeometry(self, top_rec):
        size = self.poster_list.sizeHint()
        self.poster_list.setGeometry(top_rec.x(), top_rec.y(), top_rec.width(), top_rec.height())


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
