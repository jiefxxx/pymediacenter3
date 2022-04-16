#! python3

import sys
from PyMediaCenter import pythread
from PyQt5.QtCore import Qt
from PyMediaCenter.pythread.modes import ProcessMode

from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget

from PyMediaCenter import pyconfig
from PyMediaCenter.mediaPlayer import MediaPlayer
from PyMediaCenter.medialibrary import MediaLibrary
from PyMediaCenter.medialibrary.model import ModelManager
from PyMediaCenter.server import Server
from PyMediaCenter.widget import ErrorDialog

import PyMediaCenter.resources

def configure_callback():

    pyconfig.create("server", default="192.168.1.62")
    pyconfig.create("language", default="fr_be")
    pyconfig.create("tmdb.api_key", default='bd00b4d04b286b876c3455692a531120')
    pyconfig.create("rsc.poster", default=pyconfig.get_dir("poster"))


pyconfig.load("pymediacenter", proc_name="pymediacenter-gui", callback=configure_callback)

pythread.create_new_mode(ProcessMode, "httpCom", size=4, debug=True)
pythread.create_new_mode(ProcessMode, "poster", size=2, debug=False)

MainWindowStylsheet = """ 
#mainWindow{
    border-image: url(:/rsc/background.jpg) 0 0 0 0 stretch stretch;
}
    

"""

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("PMC - PyMediaCenter")
        self.setObjectName("mainWindow")
        self.setStyleSheet(MainWindowStylsheet)

        self.model_manager = ModelManager(Server(pyconfig.get("server"), port=8000))
        self.model_manager.server.fatal_error.connect(self.on_fatal_error)

        self.setMouseTracking(True)

        self.stack = QStackedWidget(self)

        self.library = MediaLibrary(self.model_manager, self)
        self.player = MediaPlayer(self.model_manager, self)

        self.stack.addWidget(self.library)
        self.stack.addWidget(self.player)

        self.setCentralWidget(self.stack)

        self.wasMaximized = False

    def on_fatal_error(self, message):
        dlg = ErrorDialog(message, self)
        dlg.exec_()
        self.close()

    def on_switch(self, ensure=None):
        if (ensure is None or ensure == "player") and self.stack.currentWidget() == self.library:
            self.stack.setCurrentWidget(self.player)
            self.player.setFocus()
        elif (ensure is None or ensure == "library") and self.stack.currentWidget() == self.player:
            self.stack.setCurrentWidget(self.library)
            self.library.setFocus()

    def full_screen(self):
        if not self.isFullScreen():
            self.showFullScreen()
        else:
            if sys.platform.startswith('linux'):  # for Linux using the X Server
                self.showNormal()
            self.showMaximized()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.on_switch()
        if event.key() == Qt.Key_F12:
            self.full_screen()
        else:
            QMainWindow.keyPressEvent(self, event)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()

    app.exec_()
    app.closingDown()

    pythread.close_all_mode()


if __name__ == '__main__':
    main()
