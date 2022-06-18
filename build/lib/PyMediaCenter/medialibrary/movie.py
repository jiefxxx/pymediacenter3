import time

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QStyleOption, QStyle, \
    QGridLayout

from PyMediaCenter.medialibrary.mediaList import PersonWidget, MovieWidget
from PyMediaCenter.medialibrary.mediaView import PosterView, SeeView, TrailerView, LinkPerson, LinkGenre
from PyMediaCenter.medialibrary.navWidget import TopNavWidget, MenuList


class MovieListView(QFrame):
    def __init__(self, library, genre=None):
        QFrame.__init__(self, library)
        self.library = library
        self.model = library.model_manager.get_movies()

        if genre:
            self.model.set_genres([genre])
            self.model.set_sort_key("vote_average", reverse=True)

        main_box = QVBoxLayout()
        self.setLayout(main_box)
        self.top = TopNavWidget(self, self.library, menu=True)
        self.top.set_data("Film", "")
        self.top.menu.clicked.connect(self.on_menu)

        self.poster = MovieWidget(self, self.library, wrapping=True)
        self.poster.set_model(self.model)
        self.poster.setObjectName("VideoTable")

        self.menu = MenuList(self)
        self.menu.setVisible(False)

        main_box.addWidget(self.top)
        main_box.addWidget(self.menu)
        main_box.addWidget(self.poster, stretch=True)

    def on_menu(self):
        if self.menu.isVisible():
            self.menu.setVisible(False)
        else:
            self.menu.setVisible(True)

class MovieView(QFrame):
    movie_info = pyqtSignal('PyQt_PyObject')

    def __init__(self, library, movie_id):
        QFrame.__init__(self, library)
        self.movie_id = movie_id
        self.library = library
        self.setAutoFillBackground(True)

        self.pixmap_background = None

        self.poster = PosterView(self)

        self.setObjectName("mediaView")

        self.release = QLabel()
        self.release.setObjectName("ReleaseDate")

        self.vote = QLabel()
        self.vote.setObjectName("Vote")

        self.see = SeeView(self)

        self.genres_hbox = QHBoxLayout()

        self.tag_line = QLabel()
        self.tag_line.setObjectName("TagLine")
        self.tag_line.setWordWrap(True)

        self.overview = QLabel()
        self.overview.setWordWrap(True)
        self.overview.setObjectName("Overview")

        self.crews = CrewMovieView(self, self.library)

        self.trailer = TrailerView(self, self.library)

        release_hbox = QHBoxLayout()
        release_hbox.addWidget(self.vote)
        release_hbox.addStretch()
        release_hbox.addWidget(self.see)
        release_hbox.addStretch()
        release_hbox.addWidget(self.release)

        movie_vbox = QVBoxLayout()
        movie_vbox.addLayout(release_hbox)
        movie_vbox.addStretch()
        movie_vbox.addLayout(self.genres_hbox)
        movie_vbox.addStretch()
        movie_vbox.addWidget(self.tag_line)
        movie_vbox.addWidget(self.overview)
        movie_vbox.addStretch()
        movie_vbox.addWidget(self.trailer)
        movie_vbox.addStretch()
        movie_vbox.addWidget(self.crews)
        movie_vbox.addStretch()

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.poster)
        self.hbox.addLayout(movie_vbox, stretch=True)

        self.cast_view = PersonWidget(self, self.library, line=2)
        self.top = TopNavWidget(self, self.library)

        main_box = QVBoxLayout()
        main_box.addWidget(self.top)
        main_box.addLayout(self.hbox)
        main_box.addWidget(self.cast_view)

        widget = QFrame()
        widget.setLayout(main_box)

        scroll_widget = QScrollArea()
        scroll_widget.setWidgetResizable(True)
        scroll_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_widget.setWidget(widget)

        scroll_box = QVBoxLayout()
        scroll_box.addWidget(scroll_widget)
        self.setLayout(scroll_box)

        self.movie_id = None

        self.movie_info.connect(self.edit_data)
        self.poster.clicked.connect(self.person_selected)
        library.model_manager.get_movie(movie_id, self.movie_info)

    def refresh(self):
        self.library.model_manager.get_movie(self.movie_id, self.movie_info)

    def person_selected(self):
        self.library.new_videos("movie", self.movie_id)

    def edit_data(self, data):
        self.movie_id = data["id"]
        self.pixmap_background = data["backdrop"]
        self.poster.set_pixmap(data["poster"])
        self.top.set_data(data["title"], f'({data["original_title"]})')
        self.release.setText(data["release_date"])
        self.see.set_see(data["watched"])
        if len(data["tagline"]) == 0:
            self.tag_line.hide()
        else:
            self.tag_line.setText(data["tagline"])
        self.overview.setText(data["overview"])
        self.vote.setText(str(round(data["vote_average"], 1)))

        for genre in data["genres"]:
            label = LinkGenre(self, self.library, genre)
            label.setText(genre)
            label.setObjectName("Link")
            self.genres_hbox.addWidget(label)
        self.genres_hbox.addStretch()

        self.crews.set_crew(data["crew"])

        self.trailer.set_trailer(data["trailer"])

        self.cast_view.set_model(data["casting"])
        self.poster.setFocus()
        time.sleep(0.1)
        self.resize(self.size())
        self.repaint()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        if self.pixmap_background:
            p.drawPixmap(self.rect(), self.pixmap_background)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)


class CrewMovieView(QFrame):
    def __init__(self, parent, library):
        QFrame.__init__(self, parent)
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.library = library
        label_director = QLabel()
        label_director.setText("Réalisateur :")
        label_director.setObjectName("CrewTitle")
        label_screenplay = QLabel()
        label_screenplay.setText("Metteur en Scène :")
        label_screenplay.setObjectName("CrewTitle")
        label_producer = QLabel()
        label_producer.setText("Producteur :")
        label_producer.setObjectName("CrewTitle")

        self.grid_layout.addWidget(label_director, 0, 0)
        self.grid_layout.addWidget(label_screenplay, 0, 2)
        self.grid_layout.addWidget(label_producer, 0, 3)

    def set_crew(self, crews):
        hbox_producer = QHBoxLayout()
        hbox_screenplay = QHBoxLayout()
        hbox_director = QHBoxLayout()

        for crew in crews:
            label = LinkPerson(self, self.library, crew["id"], crew["name"])
            label.setObjectName("Link")
            if crew["job"] == "Producer":
                hbox_producer.addWidget(label)
            elif crew["job"] == "Screenplay":
                hbox_screenplay.addWidget(label)
            elif crew["job"] == "Director":
                hbox_director.addWidget(label)

        self.grid_layout.addLayout(hbox_producer, 1, 0)
        self.grid_layout.addLayout(hbox_screenplay, 1, 2)
        self.grid_layout.addLayout(hbox_director, 1, 3)


