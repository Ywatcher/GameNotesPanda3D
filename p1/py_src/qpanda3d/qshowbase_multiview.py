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
from .mouse_watcher import QMouseWatcherNode
# from QPanda3D import Panda3DWorld
import builtins
from datetime import datetime
from direct.showbase.ShowBase import ShowBase
from game.events import Events
from util.log import Loggable
from panda3d_game.camera_controller import CameraController, PlayerCamController
from panda3d.core import (
    WindowProperties,
    KeyboardButton,
)
from direct.task import Task
from queue import Queue as PyQueue

from direct.showbase.InputStateGlobal import inputState
from panda3d_game.app import MultiViewShowBase, ControlShowBaseMultiView

class QShowBaseMultiView(MultiViewShowBase):
    def __init__(
        self, 
        ):
        if not hasattr(self, "isQShowBaseInit"):
            self.focus = None # as previous "parent"
            MultiViewShowBase.__init__(self)
            # self.screenTexture = Texture()
            # self.buff = None
            # self.clear_color = clear_color
            self.name = name
            self._isQtStart = False
            self.isQShowBaseInit = True
            # self.size = size
            # self.cams = []
            # self.views = []
            self.mouseWatcherNode = QMouseWatcherNode()
            # self.pipe = GraphicsPipeSelection.get_global_ptr().make_pipe()

    def setFocus(self, widget:QWidget):
        self.MouseWatcherNode.setParent(widget)
        self.focus = widget

    
    def run(self):
        # FIXME
        if not self._isQtStart:
            self.win = self.make_window(
                "",
                WindowProperties(),FrameBufferProperties())
        ContextShowBase.run(self)

    def makeOffScreenBuffer(self, name, width,height,clear_color = None,sort=-100,resize_with_camera:bool=False):
        if clear_color is None:
            clear_color = self.clear_color
        super().makeOffScreenBuffer(name,width,height,clear_color,sort,resize_with_camera)



class QControlMultiView(ControlShowBaseMultiView, QShowBaseMultiView):



    def __init__(self):
        QShowBaseMultiView.__init__(self)
        if not hasattr(self, "isControlShowBaseInit"):
            self.isControlShowBaseInit = True
            self.is_cursor_in_game: bool = False
            # self.cursor_in()
            self.default_cam_pos = (0, -10, 1)
            self.display_camera.setPos(*self.default_cam_pos)
            self.key_input = KeyboardInput()
            # self.cam_controller = PlayerCamController(self.display_camera)
            # self.cam_controller.setRef(self.rdr_scene)  # FIXME: autoset
            # control ------------ FIXME
            self.buttonThrowers[0].node().setButtonDownEvent('button')
            self.buttonThrowers[0].node().setButtonUpEvent('button-up')
            # self.accept("space", lambda: print(self.camera.get_pos()))
            

            # self.accept('z', self.toggle_camera)
            # self.accept("escape", self.cursor_out)
            # self.accept("b", self.cursor_in)  # FIXME
            # self.accept('control-w', self.userExit)
            # self.accept(Events.GameEndEvent, self.userExit)
            self.taskMgr.add(self.update_camera, "update_camera_task")
            # self.taskMgr.add(self.cam_controller.update, "update_cam_controller")
            # self.taskMgr.add(self.handle_actions, "handle_actions")
            # self.delta_h = 0
            # self.delta_p = 0
            # self.delta_r = 0
        ControlShowBaseMultiView.__init__(self, False, False) # inits context showbase 

    def startQt(self):
        self.getMouseXY = self.getMouseXY_Q
        self.movePointer = self.movePointer_Q
        self.center_mouse = self.center_mouse_Q
        self.cam_sensitivity = 10
        QShowBase.startQt(self)

    def set_keyboard_input_for_controller(self, control_id):
        self.controllers[control_id].setKeyInput(self.key_input)


    def set_widget_inputs_for_controller(self, widget, control_id):
        mouse_watcher = QMouseWatcher(widget)
        self.controllers[control_id].setMouseInput(mouse_watcher)


    # def render_cam_to_widget(self, cam, widget, name):
        # # FIXME:put into gui 

        # view = self.render_cam(cam, name)
        # widget = widget(view)
        # control = Pla
        
    

    # def getMouseXY_Q(self):
        # ret= tuple(
            # self.mouseWatcherNode.getMouse()
        # )
        # return ret

    def movePointer_Q(self, device, x,y):
        # print("move")
        self.parent.movePointer(device,x,y)

    def center_mouse_Q(self):

        window_center_x = self.focus.width() // 2
        window_center_y = self.focus.height() // 2
        self.movePointer(0, window_center_x, window_center_y)
        rel_x = -1 + 2 * window_center_x / self.parent.width()
        rel_y = -1 + 2 * window_center_y / self.parent.height()
        rel_y = -rel_y
        self.prev_mouse_x = (rel_x)
        self.prev_mouse_y = (rel_y)

    def toggle_camera(self):
        pass # TODO: toggle_camera for current widget

