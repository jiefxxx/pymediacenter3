from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QSpacerItem, QScrollArea

from PyMediaCenter.medialibrary.mediaList import PosterListWidget
from PyMediaCenter.widget import QIconButton, QSelectorIcon


class HomeView(QFrame):
    home_info = pyqtSignal('PyQt_PyObject')

    def __init__(self, library):
        QFrame.__init__(self, library)
        self.library = library
        main_layout = QVBoxLayout(self)

        self.last_view = PosterListWidget(self, self.library)
        self.last_view.setObjectName("List")

        self.recent_view = PosterListWidget(self, self.library)
        self.recent_view.setObjectName("List")

        self.genre_view = PosterListWidget(self, self.library)
        self.genre_view.setObjectName("List")

        self.category = CategoryWidget(self, self.library)
        self.category.setObjectName("HomeCategory")

        main_layout.addWidget(self.genre_view)
        main_layout.addWidget(self.last_view)
        main_layout.addWidget(self.recent_view)
        main_layout.addStretch()

        widget = QFrame()
        widget.setLayout(main_layout)

        scroll_widget = QScrollArea()
        scroll_widget.setWidgetResizable(True)
        scroll_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_widget.setWidget(widget)

        scroll_box = QVBoxLayout()
        scroll_box.addWidget(self.category)
        scroll_box.addWidget(scroll_widget)
        self.setLayout(scroll_box)

        self.current_category = None

        self.home_info.connect(self.edit_data)
        self.category.category_changed.connect(self.on_category)

        self.recent_view.doubleClicked.connect(self.on_media)
        self.last_view.doubleClicked.connect(self.on_media)

        self.genre_view.doubleClicked.connect(self.on_genre)

        self.on_category("movie")

    def on_category(self, category):
        self.current_category = category
        self.library.model_manager.get_home(self.current_category, self.home_info)

    def edit_data(self, data):
        self.last_view.set_model(data["last"])
        self.recent_view.set_model(data["recent"])
        self.genre_view.set_model(data["genre"])
        self.repaint()

    def on_media(self, data):
        if self.current_category == "movie":
            self.library.new_movie_info(data["id"])
        elif self.current_category == "tv":
            self.library.new_tv_info(data["id"])

    def on_genre(self, data):
        if self.current_category == "movie":
            self.library.new_movie_list(genre=data["name"])
        elif self.current_category == "tv":
            self.library.new_tv_list(genre=data["name"])


class CategoryWidget(QFrame):
    category_changed = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent, library):
        QFrame.__init__(self, parent)
        self.library = library
        main_layout = QHBoxLayout(self)

        prog_name = QLabel("PyMediaCenter", self)
        prog_name.setObjectName("ProgName")

        prog_icon = QLabel(self)
        pixmap = QPixmap(":/rsc/logo_1.png")
        pixmap = pixmap.scaled(1000, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        prog_name.setObjectName("ProgName")
        prog_icon.setPixmap(pixmap)

        self.movie = QSelectorIcon(self,
                                   ":/rsc/movie_white.png",
                                   ":/rsc/movie_black.png",
                                   ":/rsc/movie_orange.png",
                                   96)
        self.tv = QSelectorIcon(self,
                                   ":/rsc/tv_white.png",
                                   ":/rsc/tv_black.png",
                                   ":/rsc/tv_orange.png",
                                   96)

        self.search = QIconButton(self,
                                  ":/rsc/search_white.png",
                                  ":/rsc/search_black.png",
                                  96)

        self.collection = QIconButton(self,
                                      ":/rsc/collection_white.png",
                                      ":/rsc/collection_black.png",
                                      96)

        self.exit = QIconButton(self,
                                ":/rsc/exit_white.png",
                                ":/rsc/exit_black.png",
                                96)

        self.movie.set_selected(True)
        self.movie.clicked.connect(self.on_movie)
        self.tv.set_selected(False)
        self.tv.clicked.connect(self.on_tv)
        self.search.clicked.connect(self.library.on_search)
        self.collection.clicked.connect(self.on_collection)
        self.exit.clicked.connect(self.library.on_exit)

        main_layout.addWidget(prog_icon)
        main_layout.addWidget(prog_name)
        main_layout.addSpacerItem(QSpacerItem(256, 96))
        main_layout.addWidget(self.movie)
        main_layout.addSpacerItem(QSpacerItem(64, 96))
        main_layout.addWidget(self.tv)
        main_layout.addSpacerItem(QSpacerItem(64, 96))
        main_layout.addWidget(self.search)
        main_layout.addSpacerItem(QSpacerItem(64, 96))
        main_layout.addWidget(self.collection)
        main_layout.addStretch()
        main_layout.addWidget(self.exit)

        self.setLayout(main_layout)

    def on_tv(self):
        if self.tv.selected():
            self.library.new_tv_list()
        else:
            self.movie.set_selected(False)
            self.tv.set_selected(True)
            self.category_changed.emit("tv")

    def on_movie(self):
        if self.movie.selected():
            self.library.new_movie_list()
        else:
            self.movie.set_selected(True)
            self.tv.set_selected(False)
            self.category_changed.emit("movie")

    def on_collection(self):
        pass
