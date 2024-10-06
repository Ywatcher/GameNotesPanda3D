# -*- coding: utf-8-*-
"""
edited from:
Module : Panda3DWorld
Author : Saifeddine ALOUI
Description :
    Inherit this object to create your custom world
"""
# from panda3d.core import

# PyQt imports
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from .QtGui import QCursor
from PyQt5.QtWidgets import *
# panda3d imports
from panda3d.direct import throw_new_frame, init_app_for_gui
# from panda3d.core import loadPrcFileData
# loadPrcFileData("", "window-type none") # Set Panda to draw its main window in an offscreen buffer
from direct.showbase.DirectObject import DirectObject
from panda3d.core import (
    GraphicsOutput, Texture,
    ConfigVariableManager, WindowProperties,
    LVecBase4f, FrameBufferProperties,
    GraphicsPipe
)
from panda3d_game.app.app_ import ContextShowBase, ControlShowBase
# Set up Panda environment

import platform
from QPanda3D.QMouseWatcherNode import QMouseWatcherNode
from QPanda3D import Panda3DWorld
import builtins
from datetime import datetime
from direct.showbase.ShowBase import ShowBase
from game.events import Events
from util.log import Loggable
from panda3d_game.camera_controller import CameraController, PlayerCamController
from panda3d_game.controller import PlayerController
from panda3d.core import (
    WindowProperties,
    KeyboardButton,
)
from direct.task import Task
from queue import Queue as PyQueue

from direct.showbase.InputStateGlobal import inputState

__all__ = ["QShowBase", "QControl"]


class QShowBase(ContextShowBase):
    """
    edited from Panda3DWorld
    without disabling mouse
    """
    # TODO: window properties

    def __init__(
        self,
        size=1.0,
        clear_color=LVecBase4f(0.1, 0.1, 0.1, 1),
        name="qpanda3D"
    ):
        # TODO: multi camera, multi buffer, multi window

        # TODO: two timers - use a singleton timer instead widget timer
        # call base.graphicsEngine.renderFrame() in tick()
        # implement renderframe in qshowbase
        if not hasattr(self, "isQShowBaseInit"):
            self.parent = None
            ContextShowBase.__init__(self)
            self.screenTexture = Texture()
            self.buff = None
            self.clear_color = clear_color
            self.name = name
            self._isQtStart = False
            self.isQShowBaseInit = True
            self.size = size
            self.cams = []
            # self.pipe = GraphicsPipeSelection.get_global_ptr().make_pipe()

    def startQt(self):
        if not self._isQtStart:
            clear_color = self.clear_color
            name = self.name
            size = self.size
            sort = -100
            self.screenTexture.setMinfilter(Texture.FTLinear)
            self.screenTexture.setFormat(Texture.FRgba32)
            self.screenTexture.set_wrap_u(Texture.WM_clamp)
            self.screenTexture.set_wrap_v(Texture.WM_clamp)
            buff_size_x = int(self.win.get_x_size() * size)
            buff_size_y = int(self.win.get_y_size() * size)
            winprops = WindowProperties()
            winprops.set_size(buff_size_x, buff_size_y)

            props = FrameBufferProperties()
            props.set_rgb_color(True)
            props.set_rgba_bits(8, 8, 8, 8)
            props.set_depth_bits(8)
            self.buff = self.graphicsEngine.make_output(
                self.pipe, name, sort,
                props, winprops,
                GraphicsPipe.BF_resizeable,
                self.win.get_gsg(), self.win)

            self.buff.addRenderTexture(
                self.screenTexture, GraphicsOutput.RTMCopyRam)
            self.buff.set_sort(sort)
            self.cam = self.makeCamera(self.buff)
            self.camNode = self.cam.node()
            self.camLens = self.camNode.get_lens()
            if clear_color is None:
                self.buff.set_clear_active(GraphicsOutput.RTPColor, False)
            else:
                self.buff.set_clear_color(clear_color)
                self.buff.set_clear_active(GraphicsOutput.RTPColor, True)
            # self.movePointer = self.empty
            self._isQtStart = True

    def set_parent(self, parent: QWidget):
        self.parent = parent
        self.mouseWatcherNode = QMouseWatcherNode(parent)

    def getAspectRatio(self, win = None):
        if win is None and self.parent is not None:
            return float(self.parent.width()) / float(self.parent.height())
        else:
            return super().getAspectRatio(win)

    def run(self):
        # FIXME
        if not self._isQtStart:
            self.win = self.make_window(
                "",
                WindowProperties(),FrameBufferProperties())
        ContextShowBase.run(self)

    
class QControl(ControlShowBase, QShowBase):
    def __init__(self):
        QShowBase.__init__(self)
        if not hasattr(self, "isControlShowBaseInit"):
            self.isControlShowBaseInit = True
            self.is_cursor_in_game: bool = True
            self.cursor_in()
            self.default_cam_pos = (0, -10, 1)
            self.display_camera.setPos(*self.default_cam_pos)
            self.cam_controller = PlayerCamController(self.display_camera)
            self.cam_controller.setRef(self.rdr_scene)  # FIXME: autoset
            # control ------------ FIXME
            # self.buttonThrowers[0].node().setButtonDownEvent('button')
            # self.buttonThrowers[0].node().setButtonUpEvent('button-up')
            # self.accept("space", lambda: print(self.camera.get_pos()))
            self.accept('z', self.toggle_camera)
            self.accept("escape", self.cursor_out)
            self.accept("b", self.cursor_in)  # FIXME
            self.accept('control-w', self.userExit)
            self.accept(Events.GameEndEvent, self.userExit)
            self.taskMgr.add(self.update_camera, "update_camera_task")
            self.taskMgr.add(self.cam_controller.update, "update_cam_controller")
            self.taskMgr.add(self.handle_actions, "handle_actions")
            self.delta_h = 0
            self.delta_p = 0
            self.delta_r = 0
        ControlShowBase.__init__(self, False, False)

    @property
    def flip_y_coefficient(self) -> int:
        return 2*int(self.flip_y) - 1

    def startQt(self):
        self.getMouseXY = self.getMouseXY_Q
        self.movePointer = self.movePointer_Q
        self.center_mouse = self.center_mouse_Q
        self.cam_sensitivity = 10
        QShowBase.startQt(self)

    def getMouseXY_Q(self):
        ret= tuple(
            self.mouseWatcherNode.getMouse()
        )
        return ret

    def movePointer_Q(self, device, x,y):
        # print("move")
        self.parent.movePointer(device,x,y)

    def center_mouse_Q(self):
        window_center_x = self.parent.width() // 2
        window_center_y = self.parent.height() // 2
        self.movePointer(0, window_center_x, window_center_y)
        # rel_x = -1 + 2 * pos.x() / self.parent.width()
        # rel_y = -1 + 2 * pos.y() / self.parent.height()
        rel_x = -1 + 2 * window_center_x / self.parent.width()
        rel_y = -1 + 2 * window_center_y / self.parent.height()
        rel_y = -rel_y
        self.prev_mouse_x = (rel_x)
        self.prev_mouse_y = (rel_y)

    def cursor_in(self):
        ControlShowBase.cursor_in(self)
        if self.parent is not None:
            self.parent.hideCursor()

    def cursor_out(self):
        ControlShowBase.cursor_out(self)
        if self.parent is not None:
            self.parent.showCursor()

    def set_parent(self,  parent: QWidget):
        QShowBase.set_parent(self, parent)
        if self.is_cursor_in_game:
            self.parent.hideCursor()