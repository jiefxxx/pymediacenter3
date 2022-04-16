import time

from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QFrame, QLabel, QApplication, QVBoxLayout, QHBoxLayout, QScrollArea, QStyleOption, QStyle, \
    QSizePolicy, QWidget, QGridLayout, QTableView, QAbstractItemView, QHeaderView, QSpacerItem

from PyMediaCenter.medialibrary.layout import SimpleListLayout
from PyMediaCenter.medialibrary.mediaList import  SeasonWidget, \
    PersonWidget, TvWidget
from PyMediaCenter.medialibrary.mediaView import PosterView, SeeView, TrailerView, LinkPerson, LinkGenre
from PyMediaCenter.medialibrary.navWidget import TopNavWidget, MenuList


class TvListView(QFrame):
    def __init__(self, library, genre=None):
        QFrame.__init__(self, library)
        self.library = library
        self.model = library.model_manager.get_tvs()

        if genre:
            self.model.set_genres([genre])
            self.model.set_sort_key("vote_average", reverse=True)

        main_box = QVBoxLayout()
        self.setLayout(main_box)
        self.top = TopNavWidget(self, self.library, menu=True)
        self.top.set_data("Série", "")
        self.top.menu.clicked.connect(self.on_menu)

        self.poster = TvWidget(self, self.library, wrapping=True)
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


class TvView(QFrame):
    tv_info = pyqtSignal('PyQt_PyObject')

    def __init__(self, library, tv_id):
        QFrame.__init__(self, library)
        self.tv_id = tv_id
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

        self.overview = QLabel()
        self.overview.setWordWrap(True)
        self.overview.setObjectName("Overview")

        self.crews = CrewTvView(self, self.library)

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
        self.season_view = SeasonWidget(self, self.library, line=1)

        self.top = TopNavWidget(self, self.library)

        main_box = QVBoxLayout()
        main_box.addWidget(self.top)
        main_box.addLayout(self.hbox)
        main_box.addWidget(self.season_view)
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

        self.tv_info.connect(self.edit_data)
        self.poster.clicked.connect(self.person_selected)
        library.model_manager.get_tv(tv_id, self.tv_info)

    def refresh(self):
        self.library.model_manager.get_tv(self.movie_id, self.movie_info)

    def person_selected(self):
        print("yeah")

    def edit_data(self, data):
        self.pixmap_background = data["backdrop"]
        self.poster.set_pixmap(data["poster"])
        self.top.set_data(data["title"], f'({data["original_title"]})')
        self.release.setText(data["release_date"])
        self.see.set_see(data["watched"])
        self.overview.setText(data["overview"])
        self.vote.setText(str(round(data["vote_average"], 1)))

        for genre in data["genres"]:
            label = LinkGenre(self, self.library, genre)
            label.setText(genre)
            label.setObjectName("Link")
            self.genres_hbox.addWidget(label)

        self.crews.set_crew(data["crew"])

        self.trailer.set_trailer(data["trailer"])

        self.cast_view.set_model(data["casting"])
        self.season_view.set_model(data['season'])
        self.poster.setFocus()

        self.repaint()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        if self.pixmap_background:
            p.drawPixmap(self.rect(), self.pixmap_background)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)


class SeasonView(QFrame):
    season_info = pyqtSignal('PyQt_PyObject')

    def __init__(self, library, tv_id, season_number):
        QFrame.__init__(self, library)
        self.tv_id = tv_id
        self.season_number = season_number
        self.library = library
        self.setAutoFillBackground(True)

        self.pixmap_background = None

        self.poster = PosterView(self)

        self.setObjectName("mediaView")

        self.release = QLabel()
        self.release.setObjectName("ReleaseDate")

        self.see = SeeView(self)

        self.overview = QLabel()
        self.overview.setWordWrap(True)
        self.overview.setObjectName("Overview")

        label_separator = QLabel()
        label_separator.setText("*")

        release_hbox = QHBoxLayout()
        release_hbox.addWidget(self.see)
        release_hbox.addWidget(self.release)
        release_hbox.addStretch()

        movie_vbox = QVBoxLayout()
        movie_vbox.addLayout(release_hbox)
        movie_vbox.addStretch()
        movie_vbox.addWidget(self.overview)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.poster)
        self.hbox.addLayout(movie_vbox, stretch=True)

        self.episodes_view = EpisodeTvView(self, self.library)

        self.top = TopNavWidget(self, self.library)

        main_box = QVBoxLayout()
        main_box.addWidget(self.top)
        main_box.addLayout(self.hbox)
        main_box.addWidget(self.episodes_view, stretch=True)

        widget = QFrame()
        widget.setLayout(main_box)

        scroll_widget = QScrollArea()
        scroll_widget.setWidgetResizable(True)
        scroll_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_widget.setWidget(widget)

        scroll_box = QVBoxLayout()
        scroll_box.addWidget(scroll_widget)
        self.setLayout(scroll_box)

        self.season_info.connect(self.edit_data)
        library.model_manager.get_tv_season(tv_id, season_number, self.season_info)

    def edit_data(self, data):
        self.pixmap_background = data["backdrop"]
        self.poster.set_pixmap(data["poster"])
        self.top.set_data(data["title"], f'({data["tv"]["title"]} saison {data["season_number"]})')
        self.release.setText(data["release_date"])
        self.see.set_see(data["watched"])
        self.overview.setText(data["overview"])
        self.episodes_view.set_data(data["episode"])

        self.repaint()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        if self.pixmap_background:
            p.drawPixmap(self.rect(), self.pixmap_background)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)


class EpisodeTvView(QTableView):
    def __init__(self, parent, library):
        QTableView.__init__(self, parent)
        self.library = library
        self.setSortingEnabled(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalHeader().setVisible(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setWordWrap(True)
        self.setTextElideMode(Qt.ElideNone)
        self.setIconSize(QSize(56, 56))

        self.doubleClicked.connect(self._on_selection)

    def set_data(self, data):
        self.setModel(data)
        self.horizontalHeader().setDefaultSectionSize(64)
        self.horizontalHeader().setMinimumSectionSize(64)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)


    def _on_selection(self):
        selection = self.selectionModel()
        indexes = selection.selectedIndexes()
        if len(indexes) > 0:
            data = self.model().data(indexes[0])
            if data:
                self.library.new_videos("tv", data["id"])





class CrewTvView(QFrame):
    def __init__(self, parent, library):
        QFrame.__init__(self, parent)
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.library = library
        label_creator = QLabel()
        label_creator.setText("Créateur :")
        label_creator.setObjectName("CrewTitle")

        self.grid_layout.addWidget(label_creator, 0, 0)


    def set_crew(self, crews):
        hbox_creator = QHBoxLayout()

        for crew in crews:
            label = LinkPerson(self, self.library, crew["id"], crew["name"])
            label.setObjectName("Link")
            if crew["job"] == "Creator":
                hbox_creator.addWidget(label)

        self.grid_layout.addLayout(hbox_creator, 1, 0)


