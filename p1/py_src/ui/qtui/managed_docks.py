# -*- coding: utf-8-*-
from util.env.qt_env import QtWidgets,Qt

QMainWindow  = QtWidgets.QMainWindow
QDockWidget  = QtWidgets.QDockWidget
QWidget      = QtWidgets.QWidget
QHBoxLayout  = QtWidgets.QHBoxLayout
QLabel       = QtWidgets.QLabel
# from PyQt5.QtWidgets import (
        # QMainWindow, QDockWidget,QWidget,QHBoxLayout,
        # QLabel
        # )

# from PyQt5.QtCore import Qt
from util.name_manager import managed_name

"""
Manage docks by name
provide interfaces for creating and spliting dock
"""

@managed_name(name_attr="dock_name")
class _ManagedDock(QDockWidget):
    type_name = "dock"

    @classmethod
    def _default_basename(cls):
        return cls.type_name


class ManagedDock(_ManagedDock):
    def __init__(self, title: str = None, parent=None, name: str = None):
        super().__init__(title or name or "dock", parent, name=name) 
        self._create_title_bar(title or name or "dock")

    def _create_title_bar(self, left_title: str):
        """
        custom title bar: 
        title，on left ; dock_name on right
        """
        dock_id = getattr(self, "dock_name", "unknown")  

        title_bar = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(10)

        # 左边标题
        label_title = QLabel(left_title)
        layout.addWidget(label_title, alignment=Qt.AlignLeft)

        # 右边显示 dock_name
        label_id = QLabel(dock_id)
        layout.addWidget(label_id, alignment=Qt.AlignRight)

        title_bar.setLayout(layout)
        self.setTitleBarWidget(title_bar)

    # def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        # self._closed = False  # False for minimize but not close 
        # _minimized = False

        # # listen to hide event  
        # self.visibilityChanged.connect(self._on_visibility_changed)

    # def _on_visibility_changed(self, visible):
        # # 
        # if not visible and not self._closed:
            # # to minimize 
            # pass



class ManagedDockMainWindow(QMainWindow):

    def create_dock(self, name=None,  title=None, area=None, widget=None):
        """
        Create a dock with managed name.
        """

        dock = ManagedDock(title or name or "dock", self, name=name)
        if widget is not None:
            dock.setWidget(widget)
        if area is not None:
            self.addDockWidget(area, dock)

        return dock


    def get_dock(self, name):
        """
        Retrieve dock by name
        """
        return ManagedDock.get_object(name)


    def split_dock(self, base_name, new_name, orientation=Qt.Horizontal):
        """
        Split two docks by name
        """

        base_dock = self.get_dock(base_name)
        new_dock = self.get_dock(new_name)

        if base_dock is None:
            raise ValueError(f"Dock '{base_name}' not found")

        if new_dock is None:
            raise ValueError(f"Dock '{new_name}' not found")

        self.splitDockWidget(base_dock, new_dock, orientation)

    def attach_widget(self, widget, name=None, area=None, title=None):
        """
        Put a widget into a managed dock.
        """

        dock = self.create_dock(name=name, area=area, title=title)
        dock.setWidget(widget)

        return dock

    def list_docks(self):
        return ManagedDock.all_objects()


    # life span 

    # def close_dock(self, name):
        # # hide instead of destroy
        # dock = self.get_dock(name)

        # if dock:
            # dock.hide()

    def minimize_dock(self, name):
        dock = self.get_dock(name)
        if dock:
            dock.hide()

    def move_dock(self, name, area):

        dock = self.get_dock(name)

        if dock is None:
            return

        self.removeDockWidget(dock)
        self.addDockWidget(area, dock)

    def float_dock(self, name):

        dock = self.get_dock(name)

        if dock:
            dock.setFloating(True)


    def restore_dock(self, name, area=Qt.RightDockWidgetArea):
        """
        Restore a dock from floating or minimized state back to main window.
        """
        dock = self.get_dock(name)
        if dock is None:
            return

        dock.setFloating(False)
        dock.show()
        self.addDockWidget(area, dock)
