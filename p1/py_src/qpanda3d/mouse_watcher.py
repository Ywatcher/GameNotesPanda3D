# -*- coding: utf-8-*-
"""
Module : QMouseWatcherNode
Author : Niklas Mevenkamp
Description :
    This is a MouseWatcherNode implementation that accesses
    mouse position and button states through a parent QWidget.
"""

# from PySide6.QtGui import QCursor
from util.env.qt_env import QtWidgets, QtGui
# from PyQt5.QtWidgets import QWidget
# from PyQt5.QtGui import QCursor
QWidget = QtWidgets.QWidget
QCursor = QtGui.QCursor
from panda3d.core import MouseWatcher, LPoint2


__all__ = ["QMouseWatcher"]

class QMouseWatcher(MouseWatcher):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent 

    def setParent(self,parent):
        self.parent = parent

    def getMouse(self, *args, **kwargs):
        # map global QCursor pixel position to parent Widget coordinates
        if self.hasMouse():
            cursor_pos = QCursor.pos()
            pos = self.parent.mapFromGlobal(cursor_pos)
            # print("getmouse -----")
            # print("cursorpos",cursor_pos,"getmouse",pos,"xy",int(pos.x()),int(pos.y()))
            # map absolute pixel positions to relative ones
            w = self.parent.width()
            h = self.parent.height()
            # rel_x = (-w + 2 * int(pos.x())) / w
            # (-w + 2 * int(pos.x())) = -1
            # rel_y = (-h + 2 * int(pos.y())) / h
            rel_x = int(-w/2 + pos.x()) / w 
            rel_y = int(-h/2 + pos.y()) / h
            # invert y
            rel_y = -rel_y
            # print("rel xy",rel_x,rel_y)
            # print("...",(-w/2 + pos.x()))
            # print("-----")
            return LPoint2(rel_x, rel_y)
        else:
            raise Exception("mouse watcher does not have parent")

    def hasMouse(self):
        return isinstance(self.parent, QWidget)
