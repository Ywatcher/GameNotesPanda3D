from direct.task import Task
from typing import List

from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GeomEnums,
    NodePath,

    PointLight,
    DirectionalLight,
    CardMaker,
     WindowProperties
)
from direct.showbase import DirectObject
# TODO:
# implement a PlayerController with InputState
from direct.showbase.InputStateGlobal import inputState

from util.log import Loggable


class InputSource(DirectObject.DirectObject, Loggable):

    def __init__(self):
        self._active = False

    def enactive(self):
        self._active = True

    def deactive(self):
        self._active = False


class KeyboardInput(InputSource):
    def __init__(self):
        InputSource.__init__(self)
        self.held_keys: Set[str] = set()
        # button throwers from showbase will 
        # send button and button-up events
        self.accept("button", self.key_down)
        self.accept("button-up", self.key_up)
        self.enactive()
    
    def enactive(self):
        self._active = True

    def deactive(self):
        self._active = False
        self.held_keys.clear()

    @property
    def held_keys_list(self) -> list:
        return list(self.held_keys)

    def key_down(self, button:str):
        if self._active:
        # print(button,"down") # FIXME: verbose log
            self.held_keys.add(button)
        # print("down_", self.held_keys)

    def key_up(self, button:str):
        # TODO: remove combined keys
        if self._active:
            if button in self.held_keys:
                # print(
                self.held_keys.remove(button)

    def has_key(self, button:str) -> bool:
        return button in self.held_keys

    def has_keys(self, buttons:List[str]) -> bool:
        return all([
            button in self.held_keys
            for button in buttons
        ])


from abc import ABC, abstractmethod
# from PyQt5.QtCore import QRect

class ScreenRegionInput(ABC):
    """Abstract interface to provide dynamic screen region info."""
    
    @abstractmethod
    def getW(self) -> int:
        """Return current width of the region."""
        pass

    @abstractmethod
    def getH(self) -> int:
        """Return current height of the region."""
        pass

    @abstractmethod
    def getPos(self) -> tuple[int, int]:
        """Return top-left position (x, y) in global coordinates."""
        pass

    def getCenter(self) -> tuple[float, float]:
        """Return center coordinates."""
        return (self.getPos()[0] + self.getW() / 2,
                self.getPos()[1] + self.getH() / 2)

    def getRectPoints(self) -> dict[str, tuple[int,int]]:
        """Return four corner points with consistent naming."""
        x, y = self.getPos()
        w, h = self.getW(), self.getH()
        return {
            "top_left": (x, y),
            "top_right": (x + w, y),
            "bottom_left": (x, y + h),
            "bottom_right": (x + w, y + h),
        }

