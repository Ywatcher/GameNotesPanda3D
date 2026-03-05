# -*- coding: utf-8-*-

from typing import Dict
from PyQt5.QtWidgets import (
    QWidget, QApplication, QMainWindow,
    QDockWidget, QTextEdit, QPlainTextEdit
)
from PyQt5.QtCore import QObject, QEvent,Qt
from panda3d.core import (
    loadPrcFileData
    )
import pandas as pd
from qpanda3d import (
QPanda3DWidget, 
    # QShowBase, QControl,
    QShowBaseMultiView, QControlMultiView,
    Synchronizer
)
from panda3d_game.controller import Controller


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






class MultiViewQtGUI(QMainWindow):

    def getPanda3DWidget(self, name) -> QPanda3DWidget:
        return QPanda3DWidget._name_manager.get_object(name)

    def getController(self, name) -> Controller:
        return Controller._name_manager.get_object(name)

    def activate_widget_controllers(self, widget: QPanda3DWidget):
        # TODO: wrap this 
        widget_id = widget.getID()
        rows = self.widget_control_mapping_df.index[
            self.widget_control_mapping_df["widget_id"] == widget_id
        ]
        for idx in rows:
            controller_name = self.widget_control_mapping_df.at[idx, "controller_name"]
            controller = self.getController(controller_name)
            controller.enactive()
            self.widget_control_mapping_df.at[idx, "active"] = True

    def deactivate_widget_controllers(self, widget: QPanda3DWidget):
        widget_id = widget.getID()
        rows = self.widget_control_mapping_df.index[
            self.widget_control_mapping_df["widget_id"] == widget_id
        ]
        for idx in rows:
            controller_name = self.widget_control_mapping_df.at[idx, "controller_name"]
            controller = self.getController(controller_name)
            controller.deactive()
            self.widget_control_mapping_df.at[idx, "active"] = False


    def newPanda3DWidgetOnCam(self, cam, name=None, dock=None):
        view = self.panda3d.render_cam(cam, name=name, new_view="auto")
        view_id = view.getID()
        parent_widget = self if dock is None else dock
        new_widget = QPanda3DWidget(
                view, parent=parent_widget, FPS=self.FPS, 
                widget_id=name,
                synchronizer=self.synchronizer)
        widget_id = new_widget.getID()
        self.synchronizer.addWidget(new_widget)
        if dock is not None:
            dock.setWidget(new_widget)
        # self.panda3d_widgets[name] = new_widget
        new_widget.register_qobs(self)
        controller = self.panda3d.create_controller_for_camera(
            cam, control_id=name
            # TODO: sensitivity and other stuffs (future)
        )
        control_id = controller.getID()
        self.panda3d.set_keyboard_input_for_controller(control_id)
        self.panda3d.set_widget_inputs_for_controller(new_widget, control_id)
        is_active = controller.isActive
        # -----------------------------
        # TODO put into a separate class 
        self.widget_control_mapping_df.loc[len(self.widget_control_mapping_df)] = [
            widget_id,
            control_id,
            is_active
        ]
        # -----------------------------
        return new_widget, controller



    def setFocusWidget(self, widget:QPanda3DWidget):
        previous_widget = self.current_focus_widget
        if previous_widget != widget:
            widget.setFocus()
            self.current_focus_widget = widget
            if isinstance(widget, QPanda3DWidget):
                # view = widget.panda3DView
                # self.panda3d.setFocus(view)
                # FIXME: set view 
                self.panda3d.setFocus(widget)
                print(self.panda3d.focus)
                self.panda3d.center_mouse()
                self.panda3d.cursor_in() # disables mouse, centering mouse  
                # TODO: set that row to be active
                # TODO: deactivate previous row 
                self.activate_widget_controllers(widget) 
            else:
                self.panda3d.cursor_out() # enables mouse
            if isinstance(previous_widget, QPanda3DWidget):
                self.deactivate_widget_controllers(widget)
            

    def setFocusByName(self, name:str):
        # handle by console, 
        # and get the result to parse
        widget = self.getPanda3DWidget(name)
        if widget is None: # FIXME: other invalid values
            return (-1, f"No widget named '{name}'")
            # self.console_widget.log(f"No widget named '{name}'")
        try:
            self.setFocusWidget(widget)
        except Exception as e: 
            return (-1,e)
        return 0
        

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

        self.current_focus_widget = self.focusWidget() 

        self.widget_control_mapping_df = pd.DataFrame(
                columns=[
                    "widget_id", "controller_name", "active", 
                    # "minimized"
                ])


        self.startGame()
        self.panda3d.log("game start")
        self.console = self.get_console()
        self.console_widget.console = self.console
        self.setStyleSheet(styleSheet)
        if stylesheet is not None:
            self.dock_bottom_left.setStyleSheet(stylesheet)
        self.focusFilter = FocusFilter({
            FOCUS_CONSOLE:self.console_widget,
            # FOCUS_GAME:self.panda3d_widgets["default"]
            FOCUS_GAME:self.default_widget
        })

        # self.installEventFilter(self.focusFilter)
        self.console_widget.register_qobs(self)




    def startGame(self):
        self.panda3d = self.get_game()
        self.panda3d.log("create world")
        self.synchronizer.setShowBase(self.panda3d)
        # self.pandaWidget = QPanda3DWidget(
            # self.panda3d,
            # synchronizer=self.synchronizer
        # )
        # self.synchronizer.addWidget(self.pandaWidget)
        # self.dock_top_left.setWidget(self.pandaWidget)
        # TODO: manage widgets properly in future
    
        w,c = self.newPanda3DWidgetOnCam(
                cam=self.panda3d.cam,
                name="default",
                dock=self.dock_top_left)

      
        self.setFocusWidget(w)
        self.synchronizer.start()
        self.default_widget = w # FIXME
        # self.panda_mouse_watcher = self.panda3d.mouseWatcherNode



    # todo: remove a widget

    def get_game(self) -> "MultiViewShowBase":
        raise NotImplementedError

    def get_console(self):
        raise NotImplementedError





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
