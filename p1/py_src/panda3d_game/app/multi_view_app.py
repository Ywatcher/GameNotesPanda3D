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
from panda3d_game.controller import Controller 
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
            # print("init mutlview")
            ContextShowBase.__init__(self)
            self.isMultiviewInit = True 
            self.view_manager = RenderViewManager(self)

            # self.cams = [] 
            # self.views = [] 
            # self.default_view = RenderView(self.camera, "view1", parent=self) # FIXME 
            # self.add_view(default_view)

    def render_cam(self, cam, name, new_view="auto"):
        # FIXME: if a view exists for the camera, then use the old one
        if new_view == True:
            view = self.view_manager.createViewForCamera(cam, name)
        elif new_view == False or new_view == "auto":
            # TODO: implement False
            view = self.view_manager.getOrCreateViewForCamera(cam, name)
        else: 
            raise ValueError("not implemented for new_view=",new_view)
        view.start()
        return view


    def connectToView(self):
        pass

    def render_default(self):
        # FIXME: communicate with game ui to render proper ones
        return self.render_cam(self.display_camera,"default")

    # TODO: remove view 
    # TODO: create a view

# TODO: a manager to assign control id's
     

class ControlShowBaseMultiView(MultiViewShowBase):

    # control: 
    # do not control movement of view 
    # control camera or other game assets as usual instead 

    # def getController(self, control_id)
    # def getController(self, name) -> Controller:
        # return Controller._name_manager.get_object(name)

    def register_controller(self, control_id, controller):
        # controller should have a list of functions, and a list of events 
        # accept prefix-event for controller.function 
        # and for mouse watch 
        # update_camera should be a part of controller 
        # controller has mouse watcher (?)
        self.controllers[control_id] = controller
        self.taskMgr.add(
                controller.update, f"update_controller_{control_id}",
                sort=self.sort_controller)

    def create_controller_for_camera(self,cam, control_id, sensitivity=.1, flip_x=None, flip_y=None):
        if flip_x is None:
            flip_x = self.flip_x
        if flip_y is None:
            flip_y = self.flip_y
        controller = PlayerCamController(cam, sensitivity,flip_x,flip_y,name=control_id)
        control_id = controller.getID()
        self.register_controller(control_id, controller)
        controller.setRef(self.rdr_scene)  # FIXME: if there are multiple scenes
        return controller

    def enable_controller(self, control_id):
        # FIXME: log if not found control_id
        self.controllers[control_id].enactive()

    def disable_controller(self, control_id):
        self.controllers[control_id].deactive()

    def remove_controller(self,control_id):
        # controller = self.controllers[control_id]
        self.taskMgr.remove(f"update_controller_{control_id}")
        del self.controllers[control_id]

    def __init__(self, flip_x = False, flip_y=False):
        # if not hasattr(self, 'isContextShowBaseInit'):
            # print("init context showbase")
            # ContextShowBase.__init__(self)
        if not hasattr(self, "isControlShowBaseInit"):
            MultiViewShowBase.__init__(self)
            self.isControlShowBaseInit = True
            self.controllers = {} # for each view


            # a mapping, each view id -> a intermediate controller

            self.is_cursor_in_game: bool = False 
            # self.cursor_in()
            self.default_cam_pos = (0, -10, 1)
            self.display_camera.setPos(*self.default_cam_pos)

            # self.game_controller = PlayerController()
            # self.game_controller.register_key(
            #     pattern=['control', 'w'],
            #     func=lambda:print("ehy")
            # )
            self.key_input = KeyboardInput()

            # self.cam_controller = PlayerCamController(self.display_camera)
            # self.cam_controller.setRef(self.rdr_scene)  # FIXME: autoset
            # create a cam controller and a widget for the display_camera
            # how to do it without qt?
            # control ------------
            self.buttonThrowers[0].node().setButtonDownEvent('button')
            self.buttonThrowers[0].node().setButtonUpEvent('button-up')
            # self.accept("space", lambda: print(self.camera.get_pos()))
            self.accept('z', self.toggle_camera)
            self.accept("escape", self.cursor_out)
            self.accept("b", self.cursor_in)  # FIXME
            self.accept('control-w', self.userExit)
            self.accept(Events.GameEndEvent, self.userExit)
            self.sort_controller = 100 
            self.sort_centering = 250 

            self.taskMgr.add(self.update_pointer, "update_camera_task", sort=self.sort_centering)
            # self.taskMgr.add(self.cam_controller.update, "update_cam_controller")
            self.taskMgr.add(self.handle_actions, "handle_actions",sort=300)
            # self.taskMgr.add(self.game_controller.update, "update_game_controller")
            # self.cam_sensitivity = .1
            # self.delta_h = 0
            # self.delta_p = 0
            # self.delta_r = 0
        self.flip_x = flip_x
        self.flip_y = flip_y
        # self.cursor_in()


    def cursor_in(self):
        print("cin")
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
        print("cout")
        self.enable_mouse()
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
        raise NotImplementedError

    def toggle_camera(self, control_id):
        self.controllers[control_id].mounted_camera.setPos(*self.default_cam_pos)
        self.controllers[control_id].mounted_camera.setHpr(0,0,0)

    def update_pointer(self, task):
        """updata pointer to center of screen"""
        if self.is_cursor_in_game:
            # get mouse position (unified to range(-1,1))
            self.center_mouse()
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
        except Exception as e:
            print("movePointer")
            print(e)

    def _getMouseX(self):
        return self.win.getPointer(0).getX()

    def _getMouseY(self):
        return self.win.getPointer(0).getY()

    def getMouseXY(self) -> Tuple[int, int]:
        return self._getMouseX(), self._getMouseY()

