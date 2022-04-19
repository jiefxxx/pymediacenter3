from PyMediaCenter.medialibrary.home import HomeView
from PyMediaCenter.medialibrary.movie import MovieView, MovieListView
from PyMediaCenter.medialibrary.person import PersonView
from PyMediaCenter.medialibrary.search import SearchView
from PyMediaCenter.medialibrary.tv import SeasonView, TvView, TvListView
from PyMediaCenter.medialibrary.video import VideoChooser

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
        self.model_manager.tv_info.connect(self.new_tv_info)
        self.model_manager.movie_info.connect(self.new_movie_info)
        self.model_manager.busy.connect(self._busy_handler)
        #self.new_playlist.connect(self.model_manager.get_videos_info)

        self.movie = QMovie(":/rsc/loading.gif")
        self.movie.setScaledSize(QSize(128, 128))
        self.process_label = QLabel(self)
        self.process_label.setMovie(self.movie)

        self.chooser = VideoChooser(self)

        self.stack = QStackedWidget(self)
        self.stack.addWidget(HomeView(self))

        self.main_layout = MediaLibraryLayout(self.stack, self.process_label, self.chooser, self)

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

    def reset_stack(self):
        while self.stack.count() > 1:
            w = self.stack.currentWidget()
            self.stack.removeWidget(w)
            sip.delete(w)

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
        self.reset_stack()

    def new_movie_list(self, genre=None):
        self.set_stack(MovieListView(self, genre))

    def new_tv_list(self, genre=None):
        self.set_stack(TvListView(self, genre))

    def on_search(self):
        self.set_stack(SearchView(self))

    def on_exit(self):
        self.window().close()

    def new_media_view(self, media_id, media_type):
        self.model_manager.get_media_info(media_id, media_type)

    def new_person_info(self, id):
        self.set_stack(PersonView(self, id))

    def new_movie_info(self, id):
        self.set_stack(MovieView(self, id))

    def new_tv_info(self, id):
        self.set_stack(TvView(self, id))

    def new_tv_season_info(self, id, season):
        self.set_stack(SeasonView(self, id, season))

    def new_videos(self, media_type, media_id):
        self.chooser.set_media_id(media_type, media_id)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.chooser.isVisible():
            self.chooser.setVisible(False)
        elif event.key() == Qt.Key_Escape:
            self.back_stack()
        else:
            QWidget.keyPressEvent(self, event)


MediaLibraryStylesheet = """
QFrame, QWidget{
    background-color: transparent;
    padding: 0px;
    margin: 0px;
    border: 0px;
}

MovieView, PersonView, TvView, SeasonView{
    background-color: rgba(0, 0, 0, 0.5);
    color: white;
}

HomeView, ListWidget, SearchView, MovieListView, TvListView{
    background-color: rgb(64, 64, 64);
    color: white;
}

VideoChooser, MenuList{
    border-top: 5px solid rgba(250, 70, 0, 0.5);
    border-bottom: 5px solid rgba(250, 70, 0, 0.5);
    background-color: rgb(64, 64, 64);
}

PosterListView, HListView, EpisodeTvView{
    background-color: transparent;
    color: white;
    font-size: 18pt;
}

PosterListView::item:selected:active, HListView::item:selected:active{
    background-color: rgb(250, 70, 0);
}

#Poster::focus{
    background-color: rgba(250, 70, 0, 0.5);
}

#ProgName{
    font-size: 40pt;
    font-weight: bold;
    color: rgb(250, 70, 0);
}
#HomeTitle{
    font-size: 30pt;
    color: white;
}

#VideoTable{
    background-color: rgb(96, 96, 96);
    font-size: 30pt;
    color: white;
}

QTableView::item:selected:active
{
   selection-background-color: rgba(250, 70, 0, 0.8);
}

QHeaderView::section { 
    font-size: 40pt;
    color: rgb(250, 70, 0);
    background-color: rgb(64, 64, 64);
}

#List{
    background-color: rgb(96, 96, 96);
}

#Title{
    font-size: 40pt;
    font-weight: bold;
     color: white;
}
#OriginalTitle{
    font-size: 30pt;
    font-style: italic;
    color: white;
}

#TagLine{
    font-size: 25pt;
    font-style: italic;
    color: white;
}

#Overview{
    font-size: 18pt;
    color: white;
}

#Vote{
    font-size: 35pt;
    font-weight: bold;
    color: white;
}

#Link{
    font-size: 25pt;
    color: rgb(250, 70, 0);
    font-weight: bold;
}

#Link::focus{
    color: white;
    background: rgb(250, 70, 0, 0.5);
}

#ReleaseDate{
    font-size: 30pt;
    color: white;
}

#CrewTitle{
    font-size: 25pt;
    font-weight: bold;
    color: white;
}

#SearchBar{
    font-size: 30pt;
    color: rgb(250, 70, 0);
    background-color: rgb(96, 96, 96);
}

"""