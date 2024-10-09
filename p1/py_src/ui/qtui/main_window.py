from typing import Dict
from PyQt5.QtWidgets import (
    QWidget, QApplication, QMainWindow, 
    QDockWidget, QTextEdit, QPlainTextEdit
)
from PyQt5.QtCore import QObject, QEvent,Qt
from panda3d.core import (
    loadPrcFileData
)
from qpanda3d import (
    QShowBase, QPanda3DWidget, QControl, 
    Synchronizer
)

from config.style import styleSheet
from qtutil.event import *
from util.log import *
from ui.abstract_ui import AbstractGUI
from ui.qtui.qconsole import *
from ui.qtui.qlogger import *

# class QtGUI(AbstractGUI):
#     def __init__(self) -> None:
#         super().__init__()


#         self.outFocusKeyPressEnabled = 0
#         # TODO: what does it do
#         self.keyPressEnabled = 1 # TODO: set it
#         # use command or hotkey

#     # TODO: use command to set it
#     def setOutFocusKeyPress(self, enable:bool=True):
#         self.outFocusKeyPressEnabled = enable

# class AdvancedQtGUI(QtGUI):
#     # create a menu, with buttons to start game
#     # button "new window"
#     pass

# TODO: make compatible with abstract gui

class FocusFilter(QObject):
    # TODO: move to qtutil
    def __init__(self, widgets_dict = Dict[int, QWidget]):
        QObject.__init__(self)
        self.widgets_dict = widgets_dict

    def eventFilter(self, obj, event):
        evt_type = event.type()
        if evt_type in self.widgets_dict.keys():
            self.widgets_dict[evt_type].setFocus()
        return super().eventFilter(obj, event)

class RawQtGUI(QMainWindow):
    def __init__(self, FPS=60, stylesheet=styleSheet, window_title="Three Dock Layout"):
        super().__init__()
        self.FPS = FPS
        # Create three dock widgets
        self.dock_top_left = QDockWidget("Game Camera", self)
        self.dock_bottom_left = QDockWidget("Console", self)
        self.dock_right = QDockWidget("Logger", self)
        
        # Add the docks to the main window
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_top_left)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_right)
        # Split the left dock area vertically (top and bottom)
        self.splitDockWidget(self.dock_top_left, self.dock_bottom_left, Qt.Vertical)
        self.resizeDocks([self.dock_top_left, self.dock_bottom_left], [200, 200], Qt.Vertical)
        self.setWindowTitle(window_title)
        self.resize(1600, 1200)
        self.panda3d = None
        self.synchronizer = Synchronizer(self.FPS)
        loadPrcFileData("", "window-type offscreen")
        self.console_widget = ConsoleWidget("")
        self.dock_bottom_left.setWidget(self.console_widget)
        self.log_widget = LoggerWidget("Game Logs")
        self.dock_right.setWidget(self.log_widget)
        self.log_widget.add_level(GAME_LOG)
        Loggable.add_handlers_for_all(self.log_widget.handlers[GAME_LOG]) 
        self.startGame()
        self.panda3d.log("game start")
        self.console = self.get_console()
        self.console_widget.console = self.console
        self.setStyleSheet(styleSheet)
        if stylesheet is not None:
            self.dock_bottom_left.setStyleSheet(stylesheet)
        self.focusFilter = FocusFilter({
            FOCUS_CONSOLE:self.console_widget,
            FOCUS_GAME:self.pandaWidget
        })
        self.installEventFilter(self.focusFilter)
        self.console_widget.register_qobs(self)
        self.pandaWidget.register_qobs(self)

    def startGame(self):
        # TODO: use get game()
        self.panda3d = self.get_game()
        self.panda3d.log("create world")
        self.synchronizer.setShowBase(self.panda3d)
        self.pandaWidget = QPanda3DWidget(
            self.panda3d, 
            synchronizer=self.synchronizer
        )
        self.synchronizer.addWidget(self.pandaWidget)
        self.dock_top_left.setWidget(self.pandaWidget)
        self.synchronizer.start()
        self.panda_mouse_watcher = self.panda3d.mouseWatcherNode 
        self.pandaWidget.setFocus()

    # todo: remove a widget

    def get_game(self):
        raise NotImplementedError

    def get_console(self):
        raise NotImplementedError


        
# class BufferWidget:
#     # each item has its type
#     # for example, input history or output history
#     # each has its str
#     pass

# class TextBuffer:
#     # FIXME: use a queue instead
#     # implement: write to a cache file
#     # cached queue
#     pass

# class TextBrowserWidget:
#     # browse a buffer
#     pass

# MainWindow read layout file