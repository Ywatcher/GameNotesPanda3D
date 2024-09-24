# import datetime
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


class ContextShowBase(ShowBase, Loggable):
    @property
    def display_camera(self):
        return self.camera

    @property
    def rdr_scene(self):
        return self.render
    # use context management to ensure the app
    # terminates correctly
    def __init__(self):
        if not hasattr(self, "isContextShowBaseInit"):
            if not hasattr(self, "isShowBaseInit"):
                ShowBase.__init__(self)
                self.isShowBaseInit = True
            Loggable.__init__(self)
            self.log("init ContextShowBase", "log")
            self.isContextShowBaseInit = True
            self.to_exit = False
            self.actionq = PyQueue()
        # self.taskMgr.add(self.check_exit, "check_exit")

    # @classmethod
    def remove_all_task(self):
        pass

    def __enter__(self):
        return self

    # def check_exit(self, task):
        # if self.to_exit:
            # self.userExit()
        # return Task.cont
        
    def close(self):
        self.remove_all_task()
        self.log(
            "---{} destroy at {}---".format(
                self, datetime.now()
            )
        )
        self.destroy()
        self.log(
            "---{} destroyed at {}, exit---".format(
                self, datetime.now()
            )
        )

    def __exit__(self, *args):
        self.close()

    def run(self):
        self.log(
            "---{} run(), at {}---".format(
                self, datetime.now()
            )
        )
        super().run()

    def log(self, s:str, logtype:str="print"):
        print(s)

    def __repr__(self):
        if hasattr(self, "name"):
            return self.name
        else:
            return super().__repr__()


class ControlShowBase(ContextShowBase):
    def __init__(self):
        # if not hasattr(self, 'isContextShowBaseInit'):
            # print("init context showbase")
            # ContextShowBase.__init__(self)
        if not hasattr(self, "isControlShowBaseInit"):
            ContextShowBase.__init__(self)
            self.isControlShowBaseInit = True
            self.is_cursor_in_game: bool = True
            self.cursor_in()
            self.default_cam_pos = (0, -10, 1)
            self.display_camera.setPos(*self.default_cam_pos)
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
        window_center_x = self.win.getXSize() // 2
        window_center_y = self.win.getYSize() // 2
        self.movePointer(0, window_center_x, window_center_y)
        self.prev_mouse_x = window_center_x
        self.prev_mouse_y = window_center_y

    def toggle_camera(self):
        self.display_camera.setPos(*self.default_cam_pos)
        self.display_camera.setHpr(0, 0, 0)

    def update_camera(self, task):
        """updata camera to follow mouse movement"""
        if self.mouseWatcherNode.hasMouse() and self.is_cursor_in_game:
            # get mouse position (unified to range(-1,1))
            mouse_x = self.win.getPointer(0).getX()
            mouse_y = self.win.getPointer(0).getY()
            # calculate the shift of the mouse
            delta_x = (mouse_x - self.prev_mouse_x)
            delta_y = mouse_y - self.prev_mouse_y

            # 调整摄像机的水平旋转和俯仰角度
            camera_h = self.display_camera.getH() - delta_x * 0.1
            camera_p = self.display_camera.getP() - delta_y * 0.1

            # 设置新的摄像机角度
            self.display_camera.setH(camera_h)
            self.display_camera.setP(camera_p)

            # 将鼠标指针重置到窗口的中心
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


    def movePointer(self, *args):
        try:
            self.win.movePointer(*args)
        except:
            pass

