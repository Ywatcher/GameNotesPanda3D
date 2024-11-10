# -*- coding: utf-8-*-

import logging
from PyQt5.QtWidgets import QPlainTextEdit


class QLogHandler(logging.Handler):
    def __init__(self, text_edit: QPlainTextEdit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        msg = self.format(record)
        self.text_edit.appendPlainText(msg)


class LoggerWidget(QPlainTextEdit):
    def __init__(self, title):
        # TODO: set formatter
        QPlainTextEdit.__init__(self, title)
        self.setObjectName("logger")
        self.setReadOnly(True)
        self.handlers = {}

    def add_level(self, level: int):
        if level not in self.handlers.keys():
            new_handler = QLogHandler(self)
            formatter = logging.Formatter(
                # FIXME
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            new_handler.setFormatter(formatter)
            self.handlers[level] = new_handler
