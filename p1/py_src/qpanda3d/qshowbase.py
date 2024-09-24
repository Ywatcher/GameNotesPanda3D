# -*- coding: utf-8-*-
"""
edited from:
Module : Panda3DWorld
Author : Saifeddine ALOUI
Description :
    Inherit this object to create your custom world
"""
# from panda3d.core import
from panda3d_game.app import ContextShowBase
# PyQt imports
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# Panda imports
# from panda3d.core import *
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
# Set up Panda environment
import platform
from QPanda3D.QMouseWatcherNode import QMouseWatcherNode
from QPanda3D import Panda3DWorld
import builtins


__all__ = ["QShowBase"]


class QShowBase(ContextShowBase):
    """
    edited from Panda3DWorld
    without disabling mouse
    """

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
            self.movePointer = self.empty
            self._isQtStart = True

    def empty(self,*args, **kwargs):
        pass

    def set_parent(self, parent: QWidget):
        self.parent = parent
        self.mouseWatcherNode = QMouseWatcherNode(parent)

    def getAspectRatio(self, win = None):
        if win is None and self.parent is not None:
            return float(self.parent.width()) / float(self.parent.height())
        else:
            return super().getAspectRatio(win)

class QControlShowBase:
    def __init__(self):
        pass