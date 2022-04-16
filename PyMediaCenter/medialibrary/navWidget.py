from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QStyleOption, QStyle, QFrame, QHBoxLayout, QGroupBox, \
    QCheckBox, QRadioButton

from PyMediaCenter.widget import QIconButton


class TopNavWidget(QFrame):
    def __init__(self, parent, library, menu=False):
        QFrame.__init__(self, parent)
        self.library = library
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)
        back = QIconButton(self, ":/rsc/previous_white.png", ":/rsc/previous_black.png", 56)
        back.clicked.connect(self.library.back_stack)
        home = QIconButton(self, ":/rsc/home_white.png", ":/rsc/home_black.png", 56)
        home.clicked.connect(self.library.reset_stack)
        if menu:
            self.menu = QIconButton(self, ":/rsc/menu_white.png", ":/rsc/menu_black.png", 56)

        self.title = QLabel()
        self.title.setObjectName("Title")
        # self.title.setWordWrap(True)

        self.alter = QLabel()
        self.alter.setObjectName("OriginalTitle")
        # self.original_title.setWordWrap(True)

        self.time = QLabel()

        main_layout.addWidget(back)
        main_layout.addWidget(home)
        main_layout.addStretch()
        main_layout.addWidget(self.title)
        main_layout.addWidget(self.alter)
        if menu:
            main_layout.addWidget(self.menu)

        main_layout.addStretch()
        main_layout.addWidget(self.time)

    def set_data(self, title, alter):
        self.title.setText(title)
        self.alter.setText(alter)
        self.time.setText("00:00")


class MenuList(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self, parent)
        main_box = QHBoxLayout()
        self.setLayout(main_box)

        sort_by_layout = QVBoxLayout()
        group_box_sort_key = QGroupBox("Trier par: ")
        self.check_sort_revers = QCheckBox("Inversé la sélection", self)
        self.check_sort_revers.setChecked(parent.model.reverse)
        self.check_sort_revers.stateChanged.connect(self.on_sort_revers)
        group_box_sort_key_layout = QVBoxLayout()
        self.current_key = parent.model.sort_key
        for view, data in parent.model.get_sort_keys():
            radio = QRadioButton(view)
            if data == self.current_key:
                radio.setChecked(True)
            radio.toggled.connect(lambda c, nfo=data: self.on_sort(c, nfo))
            group_box_sort_key_layout.addWidget(radio)
        group_box_sort_key_layout.addStretch()
        group_box_sort_key.setLayout(group_box_sort_key_layout)
        sort_by_layout.addWidget(group_box_sort_key)
        sort_by_layout.addWidget(self.check_sort_revers)

        main_box.addLayout(sort_by_layout)

    def sizeHint(self):
        return QSize(1400, 56)

    def on_sort(self, value, data):
        if value:
            self.parent().model.set_sort_key(data)

    def on_sort_revers(self, state):
        reverse = state == Qt.Checked
        self.parent().model.reverse(reverse)
