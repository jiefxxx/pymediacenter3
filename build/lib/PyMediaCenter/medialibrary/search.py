from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QScrollArea, QSpacerItem, QSizePolicy

from PyMediaCenter.medialibrary.mediaList import MovieWidget, TvWidget, PersonWidget
from PyMediaCenter.widget import QIconButton


class SearchView(QFrame):

    def __init__(self, library):
        QFrame.__init__(self, library)
        self.library = library

        self.widget = QFrame()
        main_layout = QVBoxLayout(self.widget)
        self.widget.setLayout(main_layout)

        self.search = SerchBarWidget(self)
        self.search.search.textEdited.connect(self.on_search)

        self.movie_label = QLabel("Film :", self)
        self.movie_label.setObjectName("HomeTitle")
        self.movie_model = library.model_manager.movie_search
        self.movie_model.set_search_string(None)
        self.poster_movie = MovieWidget(self.widget, self.library)
        self.poster_movie.set_model(self.movie_model)
        self.poster_movie.setObjectName("List")

        self.tv_label = QLabel("Série :", self)
        self.tv_label.setObjectName("HomeTitle")
        self.tv_model = library.model_manager.tv_search
        self.tv_model.set_search_string(None)
        self.poster_tv = TvWidget(self.widget, self.library)
        self.poster_tv.set_model(self.tv_model)
        self.poster_tv.setObjectName("List")

        self.person_label = QLabel("Personne :", self)
        self.person_label.setObjectName("HomeTitle")
        self.person_model = library.model_manager.person_search
        self.person_model.set_search_string(None)
        self.poster_person = PersonWidget(self.widget, self.library, line=1)
        self.poster_person.set_model(self.person_model)
        self.poster_person.setObjectName("List")


        main_layout.addWidget(self.movie_label)
        main_layout.addWidget(self.poster_movie, stretch=True)
        main_layout.addWidget(self.tv_label)
        main_layout.addWidget(self.poster_tv, stretch=True)
        main_layout.addWidget(self.person_label)
        main_layout.addWidget(self.poster_person, stretch=True)
        main_layout.addStretch()

        self.movie_label.setVisible(False)
        self.poster_movie.setVisible(False)
        self.tv_label.setVisible(False)
        self.poster_tv.setVisible(False)
        self.person_label.setVisible(False)
        self.poster_person.setVisible(False)

        self.scroll_widget = QScrollArea()
        self.scroll_widget.setWidgetResizable(True)
        self.scroll_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_widget.setWidget(self.widget)

        scroll_box = QVBoxLayout()
        scroll_box.addWidget(self.search)
        scroll_box.addWidget(self.scroll_widget, stretch=True)

        self.setLayout(scroll_box)

    def on_search(self, text):
        if len(text) >= 4:
            self.movie_model.set_search_string(text)
            self.movie_label.setVisible(self.movie_model.rowCount() > 0)
            self.poster_movie.setVisible(self.movie_model.rowCount() > 0)

            self.tv_model.set_search_string(text)
            self.tv_label.setVisible(self.tv_model.rowCount() > 0)
            self.poster_tv.setVisible(self.tv_model.rowCount() > 0)

            self.person_model.set_search_string(text)
            self.person_label.setVisible(self.person_model.rowCount() > 0)
            self.poster_person.setVisible(self.person_model.rowCount() > 0)

        else:
            self.movie_label.setVisible(False)
            self.poster_movie.setVisible(False)

            self.tv_label.setVisible(False)
            self.poster_tv.setVisible(False)

            self.person_label.setVisible(False)
            self.poster_person.setVisible(False)


class SerchBarWidget(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self, parent)
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)
        back = QIconButton(self, ":/rsc/previous_white.png", ":/rsc/previous_black.png", 56)
        back.clicked.connect(parent.library.back_stack)
        home = QIconButton(self, ":/rsc/home_white.png", ":/rsc/home_black.png", 56)
        home.clicked.connect(parent.library.reset_stack)
        search = QIconButton(self, ":/rsc/search_white.png", ":/rsc/search_black.png", 56)
        self.search = QLineEdit(self)
        self.search.setObjectName("SearchBar")

        main_layout.addWidget(back)
        main_layout.addSpacerItem(QSpacerItem(20, 56))
        main_layout.addWidget(home)
        main_layout.addSpacerItem(QSpacerItem(20, 56))
        main_layout.addWidget(self.search, stretch=True)
        main_layout.addSpacerItem(QSpacerItem(10, 56))
        main_layout.addWidget(search)
