# -*- coding: utf-8-*-

from datetime import datetime
from queue import Queue as PyQueue
from typing import Tuple

from direct.showbase.ShowBase import ShowBase
from direct.showbase.InputStateGlobal import inputState
from direct.task import Task
from panda3d.core import (
    WindowProperties,
    KeyboardButton,
)
from panda3d.core import (
    GraphicsOutput, Texture,
    ConfigVariableManager, Vec4,
    LVecBase4f, FrameBufferProperties,
    GraphicsPipe
)


from game.events import Events
from util.log import Loggable
from panda3d_game.camera_controller import (
    CameraController, PlayerCamController
)
from panda3d_game.controller import PlayerController
from .app_ import ContextShowBase
from panda3d_game.render_view.render_view import RenderViewManager, RenderView


class MultiViewShowBase(ContextShowBase):
    """
    camera is camera. 
    view traces camera and renders
    cameras are controlled by controllers
    """
    def __init__(self):
        if not hasattr(self, "isMultiviewInit"):
            ContextShowBase.__init__(self)
            self.isMultiviewInit = True 
            self.view_manager = RenderViewManager(self)
            # self.cams = [] 
            # self.views = [] 
            # self.default_view = RenderView(self.camera, "view1", parent=self) # FIXME 
            # self.add_view(default_view)

    def render_cam(self, cam, name):
        view = self.view_manager.createViewForCamera(camera, name)
        view.start()
        return view


    def connectToView(self):
        pass

    def render_default(self):
        # FIXME: communicate with game ui to render proper ones
        return self.render_cam(self.display_camera,"default")

    # TODO: remove view 
    # TODO: create a view


     

class ControlShowBaseMultiView(MultiViewShowBase):

    # control: 
    # do not control movement of view 
    # control camera or other game assets as usual instead 

    def register_controller(self, control_id, controller):
        # controller should have a list of functions, and a list of events 
        # accept prefix-event for controller.function 
        # and for mouse watch 
        # update_camera should be a part of controller 
        # controller has mouse watcher (?)

        pass


    def __init__(self, flip_x = False, flip_y=False):
        # if not hasattr(self, 'isContextShowBaseInit'):
            # print("init context showbase")
            # ContextShowBase.__init__(self)
        if not hasattr(self, "isControlShowBaseInit"):
            MultiViewShowBase.__init__(self)
            self.isControlShowBaseInit = True

            self.controllers = {} # for each view
            # a mapping, each view id -> a intermediate controller

            self.is_cursor_in_game: bool = True
            self.cursor_in()
            # self.default_cam_pos = (0, -10, 1)
            # self.display_camera.setPos(*self.default_cam_pos)

            # self.game_controller = PlayerController()
            # self.game_controller.register_key(
            #     pattern=['control', 'w'],
            #     func=lambda:print("ehy")
            # )
            self.cam_controller = PlayerCamController(self.display_camera)
            self.cam_controller.setRef(self.rdr_scene)  # FIXME: autoset
            # control ------------
            self.buttonThrowers[0].node().setButtonDownEvent('button')
            self.buttonThrowers[0].node().setButtonUpEvent('button-up')
            # self.accept("space", lambda: print(self.camera.get_pos()))
            self.accept('z', self.toggle_camera)
            self.accept("escape", self.cursor_out)
            self.accept("b", self.cursor_in)  # FIXME
            self.accept('control-w', self.userExit)
            self.accept(Events.GameEndEvent, self.userExit)

            self.taskMgr.add(self.update_camera, "update_camera_task")
            self.taskMgr.add(self.cam_controller.update, "update_cam_controller")
            self.taskMgr.add(self.handle_actions, "handle_actions")
            # self.taskMgr.add(self.game_controller.update, "update_game_controller")
            self.cam_sensitivity = .1
            self.delta_h = 0
            self.delta_p = 0
            self.delta_r = 0
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.cursor_in()

    @property
    def flip_x_coefficient(self) -> int:
        return -2*int(self.flip_x) + 1

    @property
    def flip_y_coefficient(self) -> int:
        return -2*int(self.flip_y) + 1

    # def userExit(self):
        # self.log("exit")
        # super().userExit()
        # self.log("exit finish") # FIXME

    def cursor_in(self):
        # center the mouse
        self.center_mouse()
        # disable default mouse control
        self.disable_mouse()
        # hide mouse cursor
        try:
            props = WindowProperties()
            props.setCursorHidden(True)
            self.win.requestProperties(props)
        except:  #FIXME
            pass
        # set state of the mouse,
        # which controls whether camera updates
        self.is_cursor_in_game = True

    def cursor_out(self):
        # enable default mouse control
        # self.enable_mouse()
        # show mouse cursor
        try:
            props = WindowProperties()
            props.setCursorHidden(False)
            self.win.requestProperties(props)
        except:
            pass
        # set state of the mouse,
        # which controls whether camera updates
        self.is_cursor_in_game = False

    def center_mouse(self):
        """move cursor to the center of the window"""
        pass
        # print("center mouse")
        # window_center_x = self.win.getXSize() // 2
        # window_center_y = self.win.getYSize() // 2

        # self.movePointer(0, window_center_x, window_center_y)
        # self.prev_mouse_x = window_center_x
        # self.prev_mouse_y = window_center_y
        # TODO: use a mouse pointer, which can be qt mouse pointer

    def toggle_camera(self, cam_id):
        # FIXME: put into controller
        pass
        # self.views[cam_id].setPos(*self.default_cam_pos)
        # self.views[cam_id].setHpr(0, 0, 0)

    def update_camera(self, task):
        """updata camera to follow mouse movement"""
        if self.mouseWatcherNode.hasMouse() and self.is_cursor_in_game:
            focus = 
            # get mouse position (unified to range(-1,1))
            mouse_x, mouse_y = self.getMouseXY() #FIXME
            # calculate the shift of the mouse
            delta_x = mouse_x - self.prev_mouse_x
            delta_y = mouse_y - self.prev_mouse_y

            # 调整摄像机的水平旋转和俯仰角度
            camera_h = self.display_camera.getH() - delta_x * self.cam_sensitivity * self.flip_x_coefficient
            camera_p = self.display_camera.getP() - delta_y * self.cam_sensitivity * self.flip_y_coefficient

            # 设置新的摄像机角度
            self.display_camera.setH(camera_h)
            self.display_camera.setP(camera_p)

            # 将鼠标指针重置到窗口的中心
            self.center_mouse()
            self.delta_h = delta_x * self.cam_sensitivity
            self.delta_p = delta_y * self.cam_sensitivity
        return task.cont

    def toggle_fullscreen(self):
        props = WindowProperties()
        props.setFullscreen(not self.win.isFullscreen())
        self.win.requestProperties(props)

    def handle_actions(self, task):
        # FIXME: handle events
        if not self.actionq.empty():
            try:
                action = self.actionq.get()
                # TODO: use arguments
                # TODO: log as events
                # print("action",action)
                Task.messenger.send(action)
            except Exception as e:
                self.log(str(e))
        return Task.cont


    def movePointer(self, device, x, y):
        try:
            self.win.movePointer(device,x,y)
        except:
            pass

    def _getMouseX(self):
        return self.win.getPointer(0).getX()

    def _getMouseY(self):
        return self.win.getPointer(0).getY()

    def getMouseXY(self) -> Tuple[int, int]:
        return self._getMouseX(), self._getMouseY()

