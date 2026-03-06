# -*- coding: utf-8-*-

# a camera that can fly
# from panda3d.core import PointLight, DirectionalLight
# import random
import numpy as np
from direct.task import Task
from panda3d.core import (
        Camera, PerspectiveLens,
        LVector3f
)
# controller
# player controller
# agent controller
# import gizeh as gz

from util.log import Loggable
from panda3d_game.render_view.render_view import RenderView

from typing import Union
from util.py_decorators import forward_methods_to
from panda3d_game.forwarded_attributes.camera_attributes import forwarded_camera_methods
from .controller import MouseController, KeyboardController

@forward_methods_to("camera", forwarded_camera_methods)
class CameraController(MouseController):
    
    type_name = "camctrl"

    @classmethod
    def _default_basename(cls):
        return cls.type_name
    
    from panda3d.core import (
        LVector3f,
        LQuaternionf
    )

    def __init__(
            self, camera: Union[Camera, RenderView],
            sensitivity = .1,
            flip_x = False,
            flip_y = False,
            *args, **kwargs
            ):
        MouseController.__init__(self, *args, **kwargs)
        self.camera = camera
        self.move_step = .5
        self.turn_step = 5
        self.cam_sensitivity = sensitivity
        self.delta_h = 0
        self.delta_p = 0
        self.delta_r = 0
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.use_centering = True # TODO

    def update_camera(self, task: Task):
        """Update camera to follow mouse movement"""
        if self.mouseInput.hasMouse() and self._active:
            # # get mouse position (unified to range(-1,1))

            mouse_x, mouse_y = self.getMouseXY()

            if self.use_centering and self.screenRegionInput is not None:
                # center_x, center_y = self.screenRegionInput.getCenter()
                center_x, center_y = 0,0
                self.prev_mouse_x = center_x
                self.prev_mouse_y = center_y

            # # calculate the shift of the mouse
            delta_x = mouse_x - self.prev_mouse_x
            delta_y = mouse_y - self.prev_mouse_y

            camera_h = self.camera.getH() - delta_x * self.cam_sensitivity * self.flip_x_coefficient
            camera_p = self.camera.getP() - delta_y * self.cam_sensitivity * self.flip_y_coefficient
            self.camera.setH(camera_h)
            self.camera.setP(camera_p)

            self.delta_h = delta_x * self.cam_sensitivity
            self.delta_p = delta_y * self.cam_sensitivity

            if not self.use_centering:
                self.prev_mouse_x = mouse_x
                self.prev_mouse_y = mouse_y

        return task.cont
    
    @property
    def flip_x_coefficient(self) -> int:
        return -2*int(self.flip_x) + 1

    @property
    def flip_y_coefficient(self) -> int:
        return -2*int(self.flip_y) + 1

        

    

class KeyCamController(KeyboardController, CameraController):

    

    @property
    def inputs(self):
        return [self.keyInput,self.mouseInput]

    @property
    def update_tasks(self):
        return [self.update_keyboard,self.update_camera]

    def __init__(self,camera,sensitivity=.1,flip_x=False,flip_y=False, *args, **kwargs):
        CameraController.__init__(self,camera,sensitivity,flip_x,flip_y, *args, **kwargs)
        KeyboardController.__init__(self, *args, **kwargs)

    def call_move_forward(self, task):
        self.move(task, self.move_step)

    def call_move_backward(self, task):
        self.move(task, -self.move_step)

    def call_move_left(self, task):
        new_pos = self.getPos() - self.getRight(self.ref) * self.move_step
        self.setPos(new_pos)

    def call_move_right(self, task):
        new_pos = self.getPos() + self.getRight(self.ref) * self.move_step
        self.setPos(new_pos)

    def call_move_down(self, task):
        self.move_vertically(task, -self.move_step)

    def call_move_up(self, task):
        self.move_vertically(task, self.move_step)

    def setRef(self, ref):
        self.log("---set ref---:{},{}".format(ref, type(ref)))
        self.ref = ref

    def move(self, task: Task, dist: float):
        # self.log("move {}".format(dist))
        new_pos = self.getPos() + self.getForward(self.ref) * dist
        self.setPos(new_pos)

    def getForward(self, ref) -> LVector3f:
        return self.getQuat(ref).getForward()

    def getRight(self, ref) -> LVector3f:
        return self.getQuat(ref).getRight()

    def move_vertically(self, task: Task, dist: float):
        newZ = self.getZ() + dist
        self.setZ(newZ)

    def rotate(self, task: Task, angle: float):
        new_H = self.getH() + angle
        self.setH(new_H)


    def toggle_default(self, task):
        pass


class PlayerCamController(KeyCamController,Loggable):
    def __init__(
            self, camera,  sensitivity=.1,flip_x=False,flip_y=False,
            *args, **kwargs
            ):  # TODO: input keymap dict
        KeyCamController.__init__(
                self,camera,sensitivity,flip_x,flip_y,*args, **kwargs)
        Loggable.__init__(self)
        # print("controller name:", self.name)
        # from panda3d.core import KeyboardButton
        self.key_maps = {
            'w': self.call_move_forward,
            's': self.call_move_backward,
            'a': self.call_move_left,
            'd': self.call_move_right,
            'lshift': self.call_move_up,
            'space': self.call_move_down,
            'lcontrol': self.call_move_up
        }
