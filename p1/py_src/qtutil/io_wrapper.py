# -*- coding: utf-8-*-

from PyQt5.QtWidgets import QTextEdit, QPlainTextEdit
import sys
import io


class QTextEditDevice(QTextEdit, io.TextIOWrapper):
    pass  # TODO


class QPlainTextEditDevice(QPlainTextEdit, io.TextIOWrapper):
    pass  # TODO
