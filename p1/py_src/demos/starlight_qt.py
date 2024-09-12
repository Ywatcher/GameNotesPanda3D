import sys
from PyQt5 import sip
import threading
from PyQt5 import QtWidgets, QtGui
from queue import Queue as PyQueue

from direct.task import Task
from demos.physics_room import RoomScene
from panda3d_game.app import (
    ControlShowBase, UniversalGravitySpace,
    ContextShowBase
)
import threading


class QtInterface:
    # panda3d window
    # # TODO panel : start game/end game - start menu
    # console window
    #   start console after start game
    #   TODO manual load subconsoles
    # log window

    pass
class StarScene(ContextShowBase):
    pass

class StarSceneApp(ControlShowBase, UniversalGravitySpace):
    def __init__(self):
        self.log_buffer = PyQueue()
        self.out_buffer = PyQueue()
        super().__init__()
    pass

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from panda3d.core import WindowProperties, GraphicsPipe
from direct.showbase.ShowBase import ShowBase

class PandaApp(RoomScene):
    def __init__(self, window_id,buffer=None):
        ShowBase.__init__(self, windowType='offscreen')
        self.isShowBaseInit = True
        # ContextShowBase.__init__(self)
        RoomScene.__init__(self,25,25,25)

        # 设置窗口属性以嵌入到 PyQt 窗口中
        # props = WindowProperties()
        # window_id_int = int(sip.cast(window_id, int))
        # window_id_int = int(window_id)
        # print(type(window_id), window_id)
        # print(type(window_id_int), window_id_int)
        # props.set_parent_window(window_id_int)
        # self.win.request_properties(props)
        # window_handle = self.win.get_window_handle().get_int_handle()
        # self.window_handle = window_handle
        # print(self.window_handle)
        # self.create_window(window_id)
        from panda3d.core import GraphicsBuffer, GraphicsOutput
        from panda3d.core import Texture
        # self.buffer = self.graphicsEngine.make_buffer('buffer', GraphicsOutput.RTMCopyRam)
        texture = Texture()

        # 将纹理添加到 GraphicsBuffer
        self.win.add_render_texture(texture, GraphicsBuffer.RTMCopyRam)
        self.win.set_camera(self.cam.node())
        self.graphicsEngine.render_frame()


        # texture = self.win.get_texture()
        print(texture)
        self.buffer = buffer
        self.lock = threading.Lock()
        # self.taskMgr.add(self.write_graphic_buffer, "write graphics")


    def create_window(self, window_id):
        window_id_int = int(window_id)
        wp = WindowProperties()
        wp.set_parent_window(window_id_int)  # 设置窗口 ID

        w = self.openWindow(props=wp, type='onscreen',keepCamera=True)  # 创建并打开窗口
        print(w)

    def write_graphic_buffer(self, task):
        texture = self.win.get_texture()
        pnm_image = texture.get_ram_image()
        return Task.cont



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panda3D in PyQt")
        self.setGeometry(100, 100, 800, 600)

        # 嵌入 Panda3D
        # panda_app = PandaApp(int(self.winId()))
        self.layout = QtWidgets.QVBoxLayout()
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.layout)

    def add_widget(self, widget):
        self.layout.addWidget(widget)

    def add_panda3d_widget(self, window_handle):
        self.panda_widget = QtWidgets.QWidget.createWindowContainer(
            QtGui.QWindow.fromWinId(window_handle)
        )
        self.setCentralWidget(self.panda_widget)
        # self.add_widget(self.panda_widget)


if __name__ == "__main__":
    import builtins
    import traceback

    qapp = QApplication(sys.argv)
    window = MainWindow()
    # window.show()
    window.show()
    try:
        # with PhyscRoom(25, 25, 25) as app:
        with PandaApp(window.winId()) as app:
            # console = PhyscRoomConsole(showbase=app)
            # interface = CMDInterface(console=console)
            # interface.start()
            # start a thread of app
            # window.add_panda3d_widget(app.window_handle)
            app.run()


    except Exception as e:
        print(e)
        print(traceback.format_exc())
    finally:
        if hasattr(builtins, 'base'):
            builtins.base.destroy()

    sys.exit(qapp.exec_())


# TODO: create a pure scene
# then let a new class inherit it with control and physics


# while not empty
# self.log_display.append(self.console.log_buffer.get())
# use queue so that is save between threads
#

