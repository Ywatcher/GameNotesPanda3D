# -*- coding: utf-8 -*-
from abc import ABC
from enum import Enum
from typing import Callable, Union
from util.log import Loggable
class WinType(Enum):
    PandaWindow = 0
    CmdWindow = 1

class AbstractGUI(ABC, Loggable):

    def __init__(self) -> None:
        super().__init__()
        self._manager_start_game:Union[Callable,None] = None
        self._manager_end_game:Union[Callable,None] = None

    @classmethod
    def new_window(cls):
        #TODO: return window ID
        # FIXME: type of window
        # create panda window
        # create cmd window
        pass

    def set_window_type(self, wid:int, wintype:WinType):
        pass

    def start_game(self, with_window:bool=True):
        # if with_window: start with default game window
        # else start with no window, window should be created mannually
        if self._manager_start_game is not None:
            self._manager_start_game()
        else:
            self.log("cannot start game, without start_game hooked")

    def setFocus(self, wid:int):
        pass

    def close_window(self, wid):
        # TODO: implement close for each window
        pass

    def end_game(self):
        if self._manager_end_game is not None:
            self._manager_end_game()
        else:
            self.log("cannot end game, without end_game hooked")

    def startGUI(self):
        pass





# TODO: menu logic
# goes into game or not



# commands:
#   set cabin pressure
