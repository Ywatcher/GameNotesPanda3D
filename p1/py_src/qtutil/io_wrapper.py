# -*- coding: utf-8-*-

from util.env.qt_env import QtWidgets
# from PyQt5.QtWidgets import QTextEdit, QPlainTextEdit
QTextEdit = QtWidgets.QTextEdit
QPlainTextEdit = QtWidgets.QPlainTextEdit
import sys
import io


class QTextEditDevice(QTextEdit, io.TextIOWrapper):
    pass  # TODO


class QPlainTextEditDevice(QPlainTextEdit, io.TextIOWrapper):
    pass  # TODO
