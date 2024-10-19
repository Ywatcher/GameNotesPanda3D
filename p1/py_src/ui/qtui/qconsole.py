# -*- coding: utf-8-*-

from PyQt5.QtCore import Qt, QObject, QEvent
from PyQt5.QtWidgets import QPlainTextEdit
from console import Console
from util.log import Loggable
from qtutil.qobserver import QObserved
from qtutil.event import *

class ConsoleWidget(QPlainTextEdit, Loggable, QObserved):
    def __init__(self, title, console:Console=None):
        QPlainTextEdit.__init__(self,title)
        Loggable.__init__(self,name="console")
        QObserved.__init__(self)
        self.setObjectName("console")
        self.console = console
        self.setPlaceholderText(self.prompt)
        self.prev_cursor = self.cursor_pos


    @property
    def prompt(self):
        # TODO： set prompt according to the user
        return "{game prompt} "

    @property
    def cursor_pos(self):
        return self.textCursor().position()
        # TODO: set console

    def mousePressEvent(self, event):
        # return
        pos_bfore_click = self.cursor_pos  # get current cursor
        super().mousePressEvent(event)
        pos_after_click = self.cursor_pos
        if pos_after_click < self.prev_cursor:
            cursor = self.textCursor()
            cursor.setPosition(pos_bfore_click)
            self.setTextCursor(cursor)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.put('', refresh_cursor=False, prompt=False)
            if self.console is not None:
                self.debug("handle command, cursor at",self.cursor_pos)
                self.handle_command()
            return
        elif event.key() == Qt.Key_Escape:
            # FIXME: use this only when it is jumped from game to here
            # back to the game
            evt_back_to_game = QEvent(FOCUS_GAME)
            self.send_qevent(evt_back_to_game) # send to all listeners
            return
        elif event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            # prevent from deleting prompt and history
            cursor = self.textCursor()
            selection_start = cursor.selectionStart()
            selection_end = cursor.selectionEnd()
            if selection_start < self.prev_cursor:
                return
            if event.key() == Qt.Key_Backspace:
                if self.cursor_pos <= self.prev_cursor: #FIXME
                    return
            elif event.key() == Qt.Key_Delete:
                if cursor.position() < self.prev_cursor:
                    return
        pos_bfore_click = self.cursor_pos
        super().keyPressEvent(event)
        pos_after_click = self.cursor_pos
        if pos_after_click < self.prev_cursor:
            cursor = self.textCursor()
            cursor.setPosition(pos_bfore_click)
            self.setTextCursor(cursor)

    def handle_command(self):
        command = self.toPlainText().strip()[self.prev_cursor:]
        self.debug("command is `{}`".format(command))
        if command:
            Console.parse(self.console, command)
            self.print_output()

    def print_output(self):
        if self.console.out_buffer.empty():
            self.put('') # line break
        while not self.console.out_buffer.empty():
            o = self.console.out_buffer.get()
            self.debug("output is `{}`".format(o))
            self.put(o)

    def put(
        self, s,
        linebreak=True,
        refresh_cursor=True,
        prompt=True
    ):
        """
        put new text to widget,
        with predefined behaviour
        """
        if linebreak and not s.endswith('\n'):
            s += '\n'
            if prompt:
                s+=self.prompt
        self.appendPlainText(s)
        if refresh_cursor:
            self.prev_cursor = self.cursor_pos

    def clear(self):
        super().clear(self)
        self.prev_cursor = self.cursor_pos

