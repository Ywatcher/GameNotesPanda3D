# -*- coding: utf-8-*-

# from panda3d.core import PointLight, DirectionalLight

import traceback
from abc import ABC
from typing import Set, List, Dict,Callable, Union
from datetime import datetime
import numpy as np
from direct.task import Task

# from panda3d.core import (
    # Geom,
    # GeomNode,
    # GeomTriangles,
    # GeomVertexData,
    # GeomVertexFormat,
    # GeomVertexWriter,
    # GeomEnums,
    # NodePath,

    # PointLight,
    # DirectionalLight,
    # CardMaker,
     # WindowProperties
# )
from direct.showbase import DirectObject
# TODO:
# implement a PlayerController with InputState
from direct.showbase.InputStateGlobal import inputState
from panda3d.core import MouseWatcher #, LPoint2

from util.log import Loggable
from util.name_manager import managed_name
from panda3d_game.input_source import KeyboardInput,ScreenRegionInput
from abc import ABC 

__all__ = [
    "Controller", "KeyboardController", "MouseController"
]

_add_prefix = lambda x: f"control_{x}"

@managed_name(transform=_add_prefix)
class Controller(ABC):
    @property
    def isActive(self) -> bool:
        return self._active

    def getID(self):
        return self.name

    @property
    def inputs(self):
        return NotImplemented

    def __init__(self):
        if not hasattr(self,"_active"):
            self._active = False

    def enactive(self):
        self._active = True
        # for i in self.inputs:
            # try:
                # i.enactive()
            # except:
                # pass

    def deactive(self):
        self._active = False
        # for i in self.inputs:
            # try:
                # i.deactive()
            # except:
                # pass

    @property
    def update_tasks(self) -> List[Callable]:
        return [] 

    def update(self, task:Task):
        if not self._active:
            return Task.cont
        for func in self.update_tasks:
            try:
                result = func(task)

                # 如果某个 task 想终止更新循环
                if result == Task.done:
                    return Task.done

            except Exception as e:
                # 如果子类有 log 方法就用它
                if hasattr(self, "log"):
                    self.log(f"--- exception in update task {func.__name__} ---")
                    self.log(e)
                    self.log(traceback.format_exc())
                    self.log("-----------------------------------------------")
                else:
                    print(f"Exception in {func.__name__}:", e)
                    print(traceback.format_exc())

        return Task.cont

    

class KeyboardController(Controller):
    @property
    def inputs(self):
        return [self.keyInput]

    # another way is to use dict
    def __init__(self, *args, **kwargs):
        Controller.__init__(self,*args, **kwargs)
        self.key_str_sep = '\;'
        self.key_maps: Dict[str, Callable] = {}
        self.keyInput:KeyboardInput = None 

    def setKeyInput(self, key_input:KeyboardInput):
        self.keyInput = key_input

        # FIXME: dict[str, list[str], call] to avoid splitting during game

    def is_valid_pattern(self, pattern:str) -> bool:
        # TODO: implement
        return True

            # self.held_keys.clear()

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

    def update_keyboard(self, task:Task):
        # FIXME: update key for all input sources
        # let pointerInput return false for has_keys
        # FIXME: 
        # handle controdict inputs  
        
        for pattern, func in self.key_maps.items():
            if self.keyInput.has_keys(pattern.split(self.key_str_sep)):

                try:
                    func(task)
                except Exception as e:
                    self.log("---got exception when executing {}---".format(pattern))
                    self.log(e)
                    self.log(traceback.format_exc())
                    self.log("-------------------------------------")
                    raise e # FIXME
        return Task.cont

    @property
    def update_tasks(self):
        return [self.update_keyboard]


class MouseController(Controller):
    @property
    def inputs(self):
        return [self.mouseInput, self.screenRegionInput]

    @property
    def update_tasks(self):
        return [self.update_mouse]

    # another way is to use dict
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.inputs = []
        self.mouseInput:MouseWatcher = None 
        self.screenRegionInput: ScreenRegionInput = None 

    def setMouseInput(self, mouse_input:MouseWatcher):
        self.mouseInput = mouse_input

    def setScreenRegionInput(self,  screenRegionInput:ScreenRegionInput):
        self.screenRegionInput = screenRegionInput
        center_x, center_y = self.screenRegionInput.getCenter()
        self.prev_mouse_x = center_x
        self.prev_mouse_y = center_y

    def getMouseXY(self):
        ret= tuple(
            self.mouseInput.getMouse()
        )
        return ret

    def update_mouse(self, task:Task):
        return NotImplemented

       



    
