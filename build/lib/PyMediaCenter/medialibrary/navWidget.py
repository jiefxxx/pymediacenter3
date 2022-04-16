from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QStyleOption, QStyle, QFrame

from PyMediaCenter.widget import QIconButton


def add_labels(parent, layout, string_list):
    for string in string_list:
        label = QLabel(parent)
        label.setText(string)
        layout.addWidget(label)


class NavWidget(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self, parent)
        main_layout = QVBoxLayout(self)
        self.home = QIconButton([":/rsc/home_white.png", ":/rsc/home_black.png"], height=1000)
        main_layout.addWidget(self.home)
        self.movie = QIconButton([":/rsc/movie_white.png", ":/rsc/movie_black.png"], height=1000)
        main_layout.addWidget(self.movie)
        self.tv = QIconButton([":/rsc/tv_white.png", ":/rsc/tv_black.png"], height=1000)
        main_layout.addWidget(self.tv)
        self.genre = QIconButton([":/rsc/genre_white.png", ":/rsc/genre_black.png"], height=1000)
        main_layout.addWidget(self.genre)

        main_layout.addStretch()

        self.exit = QIconButton([":/rsc/exit_white.png", ":/rsc/exit_black.png"], height=1000)
        main_layout.addWidget(self.exit)

        self.setLayout(main_layout)






