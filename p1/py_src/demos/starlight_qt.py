import sys
import threading
from PyQt5 import QtWidgets
from queue import Queue as PyQueue
from panda3d_game.app import (
    ControlShowBase, UniversalGravitySpace,
    ContextShowBase
)



class QtInterface:
    # panda3d window
    # # TODO panel : start game/end game - start menu
    # console window
    #   start console after start game
    #   TODO manual load subconsoles
    # log window

    pass
class StarScene(ContextShowBase):
    pass

class StarSceneApp(ControlShowBase, UniversalGravitySpace):
    def __init__(self):
        self.log_buffer = PyQueue()
        self.out_buffer = PyQueue()
        super().__init__()
    pass

# TODO: create a pure scene
# then let a new class inherit it with control and physics


# while not empty
# self.log_display.append(self.console.log_buffer.get())
# use queue so that is save between threads
#

