import time

from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QFrame, QListView, QVBoxLayout, QSizePolicy, QLabel, QHBoxLayout, QScrollArea, QStyleOption, \
    QStyle

from PyMediaCenter.medialibrary.layout import SimpleListLayout
from PyMediaCenter.medialibrary.mediaList import PosterListWidget, MovieWidget, TvWidget
from PyMediaCenter.medialibrary.mediaView import PosterView
from PyMediaCenter.medialibrary.navWidget import TopNavWidget


class PersonView(QFrame):
    person_info = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, parent, person_id):
        QFrame.__init__(self, parent)
        self.library = parent
        self.person_id = person_id
        self.setAutoFillBackground(True)
        self.pixmap_background = None

        self.poster = PosterView(self)

        self.setObjectName("mediaView")

        self.know_for = QLabel()
        self.know_for.setObjectName("OriginalTitle")

        self.birth_and_death = QLabel()
        self.birth_and_death.setObjectName("TagLine")

        self.biography = QLabel()
        self.biography.setWordWrap(True)
        self.biography.setObjectName("Overview")

        movie_vbox = QVBoxLayout()
        movie_vbox.addWidget(self.know_for)
        movie_vbox.addStretch()
        movie_vbox.addWidget(self.birth_and_death)
        movie_vbox.addStretch()
        movie_vbox.addWidget(self.biography)
        movie_vbox.addStretch()

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.poster)
        self.hbox.addLayout(movie_vbox, stretch=True)

        self.movie_view = MovieWidget(self, self.library)
        self.tv_view = TvWidget(self, self.library)
        self.top = TopNavWidget(self, self.library)

        main_box = QVBoxLayout()
        main_box.addWidget(self.top)
        main_box.addLayout(self.hbox)
        main_box.addWidget(self.movie_view)
        main_box.addWidget(self.tv_view)

        widget = QFrame()
        widget.setLayout(main_box)

        scroll_widget = QScrollArea()
        scroll_widget.setWidgetResizable(True)
        scroll_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_widget.setWidget(widget)

        scroll_box = QVBoxLayout()
        scroll_box.addWidget(scroll_widget)
        self.setLayout(scroll_box)

        self.person_info.connect(self.edit_data)
        self.library.model_manager.get_person(person_id, self.person_info)

    def edit_data(self, data, backdrop):
        self.pixmap_background = backdrop
        self.poster.set_pixmap(data["profile"])
        self.top.set_data(data["name"], "")
        self.know_for.setText(data["known_for_department"])
        if len(data["deathday"]) == 0:
            self.birth_and_death.setText(f"Né à {data['place_of_birth']} le {data['birthday']}")
        else:
            self.birth_and_death.setText(f"Né à {data['place_of_birth']} le {data['birthday']} et mort le {data['deathday']}")
        self.biography.setText(data["biography"])
        self.movie_view.set_model(data["movie"])
        self.tv_view.set_model(data["tv"])

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

