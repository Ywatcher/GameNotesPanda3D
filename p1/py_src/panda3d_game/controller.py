# -*- coding: utf-8-*-

# from panda3d.core import PointLight, DirectionalLight

import traceback
from abc import ABC
from typing import Set, List, Dict,Callable, Union
from datetime import datetime
import numpy as np
from direct.task import Task

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



class PlayerController(DirectObject.DirectObject, Loggable):
    # another way is to use dict
    def __init__(self):
        super().__init__()
        self.key_str_sep = '\;'
        self.held_keys: Set[str] = set()
        self.key_maps: Dict[str, Callable] = {}
        self.accept("button", self.key_down)
        self.accept("button-up", self.key_up)
        self._active = True
        self.enactive()
        # FIXME: dict[str, list[str], call] to avoid splitting during game

    def is_valid_pattern(self, pattern:str) -> bool:
        # TODO: implement
        return True

    def enactive(self):
        self._active = True

    def deactive(self):
        self._active = False
        self.held_keys.clear()

    def register_key(self, pattern:Union[List[str],str], func:Callable[[Task],object]):
        if isinstance(pattern, list):
            pattern = self.key_str_sep.join(pattern)
        if not self.is_valid_pattern(pattern):
            self.log(
                "---`{}` is not a valid pattern, register failed at {}---".format(
                    pattern, datetime.now
                )
            )
        elif not isinstance(func, Callable):
            self.log(
                "---func expected to be Callable, got {}, register failed at {}---".format(
                    type(func), datetime.now
                )
            )
        else:
            # TODO: confirm to overwrite
            self.key_maps.update({pattern: func})

    @property
    def held_keys_list(self) -> list:
        return list(self.held_keys)

    def key_down(self, button:str):
        # print(button,"down") # FIXME: verbose log
        self.held_keys.add(button)
        # print("down_", self.held_keys)

    def key_up(self, button:str):
        # TODO: remove combined keys
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

    def update(self, task:Task):
        for pattern, func in self.key_maps.items():
            if self.has_keys(pattern.split(self.key_str_sep)):

                try:
                    func(task)
                except Exception as e:
                    self.log("---got exception when executing {}---".format(pattern))
                    self.log(e)
                    self.log(traceback.format_exc())
                    self.log("-------------------------------------")
        return Task.cont
