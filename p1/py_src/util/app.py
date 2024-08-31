# import datetime
from datetime import datetime
from direct.showbase.ShowBase import ShowBase
from util.log import Loggable
from game.camera_controller import CameraController, PlayerCamController
from game.controller import PlayerController
from panda3d.core import (
    WindowProperties,
    KeyboardButton
)
from direct.showbase.InputStateGlobal import inputState


class ContextShowBase(ShowBase, Loggable):
    # use context management to ensure the app
    # terminates correctly
    def __init__(self):
        super().__init__()
        self.isContextShowBaseInit = True
    
    # @classmethod
    def remove_all_task(self):
        pass
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
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
        
    def run(self):
        self.log(
            "---{} run(), at {}---".format(
                self, datetime.now()
            )
        )
        super().run()
        
    def log(self, s:str):
        print(s)
        
    def __repr__(self):
        if hasattr(self, "name"):
            return self.name
        else:
            return super().__repr__()
        
        
   
        
        
class ControlShowBase(ContextShowBase):
    @property
    def display_camera(self):
        return self.camera
    
    @property
    def rdr_scene(self):
        return self.render
    
    def __init__(self):
        if not hasattr(self, 'isContextShowBaseInit'):
            print("init context showbase")
            super().__init__()
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
        self.accept('control-w',self.userExit)
        
        self.taskMgr.add(self.update_camera, "update_camera_task")
        self.taskMgr.add(self.cam_controller.update, "update_cam_controller")
        # self.taskMgr.add(self.game_controller.update, "update_game_controller")
        
    def userExit(self):
        self.log("exit")
        super().userExit()
        
    def cursor_in(self):
        # center the mouse
        self.center_mouse()
        # disable default mouse control
        self.disable_mouse()
        # hide mouse cursor
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)
        # set state of the mouse,
        # which controls whether camera updates
        self.is_cursor_in_game = True
        
    def cursor_out(self):
        # enable default mouse control
        self.enable_mouse()
        # show mouse cursor
        props = WindowProperties()
        props.setCursorHidden(False)
        self.win.requestProperties(props)
        # set state of the mouse,
        # which controls whether camera updates
        self.is_cursor_in_game = False

    def center_mouse(self):
        """将鼠标指针重置到窗口的中心"""
        window_center_x = self.win.getXSize() // 2
        window_center_y = self.win.getYSize() // 2
        self.win.movePointer(0, window_center_x, window_center_y)
        self.prev_mouse_x = window_center_x
        self.prev_mouse_y = window_center_y
        
    def toggle_camera(self):
        self.camera.setPos(*self.default_cam_pos)
        self.camera.setHpr(0, 0, 0)

    def update_camera(self, task):
        """每帧更新摄像机的方向，使其跟随鼠标的移动"""
        if self.mouseWatcherNode.hasMouse() and self.is_cursor_in_game:
            # 获取鼠标的位置（归一化的 -1 到 1 范围内）
            mouse_x = self.win.getPointer(0).getX()
            mouse_y = self.win.getPointer(0).getY()

            # 计算鼠标移动的增量
            delta_x = (mouse_x - self.prev_mouse_x)
            delta_y = mouse_y - self.prev_mouse_y

            # 调整摄像机的水平旋转和俯仰角度
            camera_h = self.camera.getH() - delta_x * 0.1
            camera_p = self.camera.getP() - delta_y * 0.1

            # 设置新的摄像机角度
            self.camera.setH(camera_h)
            self.camera.setP(camera_p)

            # 将鼠标指针重置到窗口的中心
            self.center_mouse()
        return task.cont

    def toggle_fullscreen(self):
        props = WindowProperties()
        props.setFullscreen(not self.win.isFullscreen())
        self.win.requestProperties(props)