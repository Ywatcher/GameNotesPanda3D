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

