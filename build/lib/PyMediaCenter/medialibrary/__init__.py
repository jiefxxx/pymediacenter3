
try:
    # new location for sip
    # https://www.riverbankcomputing.com/static/Docs/PyQt5/incompatibilities.html#pyqt-v5-11
    from PyQt5 import sip
except ImportError:
    import sip

from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QWidget, QStackedWidget, QLabel

from PyMediaCenter.medialibrary.layout import MediaLibraryLayout
from PyMediaCenter.medialibrary.mediaList import MediaList, GenreList
from PyMediaCenter.medialibrary.mediaView import MovieView, TvView
from PyMediaCenter.medialibrary.navWidget import NavWidget

MEDIA_TYPE_UNKNOWN = 0
MEDIA_TYPE_MOVIE = 1
MEDIA_TYPE_TV = 2
MEDIA_TYPE_ALL = 3


class MediaLibrary(QWidget):
    new_playlist = pyqtSignal('PyQt_PyObject')

    def __init__(self, model_manager, parent):
        QWidget.__init__(self, parent)
        self.setStyleSheet(MediaLibraryStylesheet)

        self.model_manager = model_manager
        self.model_manager.tv_info.connect(self._new_tv_info)
        self.model_manager.movie_info.connect(self._new_movie_info)
        self.model_manager.busy.connect(self._busy_handler)
        self.new_playlist.connect(self.model_manager.get_videos_info)


        self.movie = QMovie(":/rsc/loading.gif")
        self.movie.setScaledSize(QSize(128, 128))
        self.process_label = QLabel(self)
        self.process_label.setMovie(self.movie)


        self.stack = QStackedWidget(self)
        self.stack.addWidget(MediaList(self, self.model_manager.get_all_media()))
        self.nav = NavWidget(self)
        self.nav.home.clicked.connect(self.on_home)
        self.nav.movie.clicked.connect(self.on_movie)
        self.nav.tv.clicked.connect(self.on_tv)
        self.nav.genre.clicked.connect(self.on_genre)
        self.nav.exit.clicked.connect(self.on_exit)

        self.main_layout = MediaLibraryLayout(self.stack, self.nav, self.process_label, self)

        self.setLayout(self.main_layout)

        self.model_manager.refresh_media()

    def on_new_playlist(self, playlist):
        print("playlist", playlist)

    def _busy_handler(self, busy):
        if busy:
            self.movie.start()
            self.process_label.setVisible(True)
        else:
            self.movie.stop()
            self.process_label.setVisible(False)

    def reset_stack(self, widget):
        while self.stack.count() > 0:
            w = self.stack.currentWidget()
            self.stack.removeWidget(w)
            sip.delete(w)
        self.set_stack(widget)

    def set_stack(self, widget):
        self.stack.addWidget(widget)
        self.stack.setCurrentIndex(self.stack.count()-1)
        widget.setFocus()

    def back_stack(self):
        if self.stack.count() > 1:
            w = self.stack.currentWidget()
            self.stack.removeWidget(w)
            sip.delete(w)

    def on_home(self):
        self.reset_stack(MediaList(self, self.model_manager.get_all_media()))

    def on_movie(self):
        self.reset_stack(MediaList(self, self.model_manager.get_movie()))

    def on_tv(self):
        self.reset_stack(MediaList(self, self.model_manager.get_tv()))

    def on_genre(self):
        self.reset_stack(GenreList(self, self.model_manager.get_genre()))

    def on_exit(self):
        self.window().close()

    def new_media_genre_list(self, genre):
        self.set_stack(MediaList(self, self.model_manager.get_all_media(genre=genre)))

    def new_media_view(self, media_id, media_type):
        self.model_manager.get_media_info(media_id, media_type)

    def _new_movie_info(self, data):
        self.set_stack(MovieView(self, data))

    def _new_tv_info(self, data):
        self.set_stack(TvView(self, data))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.back_stack()
        else:
            QWidget.keyPressEvent(self, event)


MediaLibraryStylesheet = """
QFrame{
    background-color: transparent;
}
NavWidget{
    background-color: rgba(231, 62, 1, 0.9);
    color: white;
    border-style: outset;
    border-right-color: white;
    border-right-width: 2px;
}

ListWidget, MediaView{
    background-color: rgba(0, 0, 0, 0.5);
    color: white;
    border: 0px outset black;
    padding: 0px;
    margin: 0px;
}

PosterListView{
    background-color: transparent;
    color: white;
    border: 0px outset black;
    margin: 0px;
    padding: 0px;
}

PosterListView::item:selected:active{
    border: 3px solid rgb(231, 62, 1);
    background: rgb(231, 62, 1);
}


SearchLine, CtrlListWidget{
    background-color: rgba(231, 62, 1, 0.5);
    color: white;
    font-size: 20pt;
    border: 2px outset black;
}

QComboBox, QCheckBox {
    selection-background-color: lightgray;
    background-color: transparent;
    font-size: 25pt;
    color: white;
}
QComboBox::item:selected{
    background-color: lightgray;
    color: white;
}
QComboBox QAbstractItemView {
    border: 2px solid black;
    color: white;
    selection-background-color: gray;
    background-color: rgba(231, 62, 1, 0.8);
    
}
QLabel{
    color: white;
    font-size: 15pt;
}

TvItemDescription{
    border: 0px outset white;
    background-color: transparent;
    color: white;
}
SeasonListView{
    border: 0px outset white;
    background-color: transparent;
    selection-background-color:  rgb(231, 62, 1); 
    color: white;
    font-size: 15pt;
    gridline-color: transparent;
}

SeasonListView QTableCornerButton::section{
    background-color: transparent;
    border: 0px outset white;
}

QScrollArea{
    border: 0px outset white;
}

#Title{
    font-size: 30pt;
    font-weight: bold;
}
#OriginalTitle{
    font-size: 25pt;
    font-style: italic;
}

#RowItemClicked{
    border: 2px outset black;
    background-color: rgba(255, 255, 255, 0.5);
    color: black;
}

#RowItemBase{
    border: 2px outset white;
    background-color: rgba(0, 0, 0, 0.5);
    color: white;
}

#RowItemSelected{
    border: 2px outset white;
    background-color:  rgb(231, 62, 1);
    color: white;
}

#EpisodeRowClicked{
    border-bottom: 2px outset black;
    background-color: rgba(255, 255, 255, 0.5);
    color: black;
}

#EpisodeRowBase{
    border-bottom: 2px outset white;
    background-color: transparent;
    color: white;
}

#EpisodeRowSelected{
    border-bottom: 2px outset black;
    background-color: rgb(231, 62, 1);
    color: black;
}
"""