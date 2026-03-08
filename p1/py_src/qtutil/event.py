# -*- coding: utf-8-*-

from util.env.qt_env import QT_BINDING, QtCore
# from QtCore import QEvent
QEvent = QtCore.QEvent
FOCUS_CONSOLE = QEvent.Type(QEvent.registerEventType())
FOCUS_GAME    = QEvent.Type(QEvent.registerEventType())
