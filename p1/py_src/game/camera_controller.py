# TODO: a room with walls
# a camera that can fly
# from panda3d.core import PointLight, DirectionalLight
from util.log import Loggable
from direct.task import Task

from game.controller import PlayerController

# controller
# player controller
# agent controller
from panda3d.core import Camera, PerspectiveLens

import numpy as np
# import gizeh as gz
import random


class CameraController:
    from panda3d.core import (
        LVector3f,
        LQuaternionf
    )

    def __init__(self, camera: Camera):
        self.camera = camera
        self.move_step = .5
        self.turn_step = 5
    # FIXME: use dict

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

    def setPos(self, *args):
        self.camera.setPos(*args)

    def setHpr(self, *args):
        self.camera.setHpr(*args)

    def setH(self, *args):
        self.camera.setH(*args)

    def setP(self, *args):
        self.camera.setP(*args)

    def setR(self, *args):
        self.camera.setR(*args)

    def setZ(self, *args):
        self.camera.setZ(*args)

    def getQuat(self, *args):
        return self.camera.getQuat(*args)

    def getPos(self, *args):
        return self.camera.getPos(*args)

    def getZ(self, *args):
        return self.camera.getZ(*args)

    def toggle_default(self, task):
        pass


class PlayerCamController(CameraController, PlayerController):
    def __init__(self, camera):  # TODO: input keymap dict
        CameraController.__init__(self, camera)  # TODO
        PlayerController.__init__(self)
        # from panda3d.core import KeyboardButton
        self.key_maps = {
            'w': self.call_move_forward,
            's': self.call_move_backward,
            'a': self.call_move_left,
            'd': self.call_move_right,
            'lshift': self.call_move_up,
            'space': self.call_move_down
        }
