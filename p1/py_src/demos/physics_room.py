# TODO: a room with walls
from threading import Thread, Lock
from panda3d.bullet import BulletWorld
from sympy import arg
from console.console import Console
from panda3d_game.app import ContextShowBase, ControlShowBase, PhysicsShowBase
from util.log import Loggable
from direct.task import Task
from direct.showbase.DirectObject import DirectObject

from art.basic import (
    create_sphere_node,
)
from panda3d.core import (
    NodePath,
    CardMaker,
    Texture,
    CardMaker,
    Point2,
    Vec3
)
from panda3d_game.game_object import GameObject

from util.texture import (
    np2texture
)
from art.textures.checkboard import(
    create_color_checkerboard,
)
from typing import Set, List, Dict, Callable, Union
from game.events import Events
from console import PhyscRoomConsole



def make_wall_texture(
    # make a checkerboard texture for walls
    w, h,
    square_size: float = 1,
    res: int = 8,
    color1=[0, 0, 0],
    color2=[255, 255, 255],
    name=None
) -> Texture:
    w_img = int(w*res)
    h_img = int(h*res)
    square_size_img = int(square_size*res)
    checkerboard_arr = create_color_checkerboard(
        size=(h_img, w_img),
        square_size=square_size_img,
        color1=color1, color2=color2
    )[:, :, ::-1]
    t = np2texture(
        arr=checkerboard_arr,
        format_=Texture.F_rgb,
        name=name
    )
    return t

class RoomScene(ContextShowBase):
    def __init__(self, xb: int, yb: int, zb: int):
        ContextShowBase.__init__(self)
        resolution = 8  # 8pxs a grid
        tex_top = make_wall_texture(
            yb*2, xb*2, square_size=5,
            res=resolution,
            color1=[135, 206, 235]  # celestial
        )
        tex_bot = make_wall_texture(
            yb*2, xb*2, square_size=5,
            res=resolution,
            color1=[227, 189, 101],  # mustard
            color2=[34, 139, 34]  # grass
        )
        tex_xz = make_wall_texture(
            zb*2, xb*2, square_size=5,
            res=resolution,
            color1=[255, 187, 255]  # plum
        )
        tex_yz = make_wall_texture(
            zb*2, yb*2, square_size=5,
            res=resolution,
            color1=[0, 173, 131],  # Pantone,
        )

        # maka a room
        cardxy = CardMaker('wallxy')
        cardxy.setFrame(-xb, xb, -yb, yb)
        # FIXME
        cardxy.setUvRange(Point2(0, 1),  # ll
                          Point2(1, 1),  # lr
                          Point2(1, 0),  # ur
                          Point2(0, 0))  # ul
        wall_xy_top = self.rdr_scene.attach_new_node(cardxy.generate())
        wall_xy_top.set_pos(0, 0, zb)
        wall_xy_top.setP(90)
        wall_xy_top.set_texture(tex_top)
        wall_xy_bot = self.rdr_scene.attach_new_node(cardxy.generate())
        wall_xy_bot.set_pos(0, 0, -zb)
        wall_xy_bot.setP(-90)
        wall_xy_bot.set_texture(tex_bot)
        cardxz = CardMaker('wallxz')
        cardxz.setFrame(-xb, xb, -zb, zb)
        cardxz.setUvRange(Point2(0, 1),  # ll
                          Point2(1, 1),  # lr
                          Point2(1, 0),  # ur
                          Point2(0, 0))
        wall_xz_front = self.rdr_scene.attach_new_node(cardxz.generate())
        wall_xz_front.set_pos(0, yb, 0)
        wall_xz_front.set_texture(tex_xz)
        wall_xz_back = self.rdr_scene.attach_new_node(cardxz.generate())
        wall_xz_back.set_pos(0, -yb, 0)
        wall_xz_back.setH(-180)
        wall_xz_back.set_texture(tex_xz)
        cardyz = CardMaker('wallyz')
        cardyz.setFrame(-yb, yb, -zb, zb)
        cardyz.setUvRange(Point2(0, 1),  # ll
                          Point2(1, 1),  # lr
                          Point2(1, 0),  # ur
                          Point2(0, 0))
        wall_yz_left = self.rdr_scene.attach_new_node(cardyz.generate())
        wall_yz_left.set_pos(-xb, 0, 0)
        wall_yz_left.setH(90)
        wall_yz_left.set_texture(tex_yz)
        wall_yz_right = self.rdr_scene.attach_new_node(cardyz.generate())
        wall_yz_right.set_pos(xb, 0, 0)
        wall_yz_right.setH(-90)
        wall_yz_right.set_texture(tex_yz)

        sphere_o = create_sphere_node("o", 12, 12)
        self.rdr_scene.attachNewNode(sphere_o)
        node_path_sphere_o = NodePath(sphere_o)
        node_path_sphere_o.setColor((1, 1, 1, 1))
        node_path_sphere_o.setPos(0, 0, 0)
        sphere_x = create_sphere_node("x", 12, 12)
        self.rdr_scene.attachNewNode(sphere_x)
        node_path_sphere_x = NodePath(sphere_x)
        node_path_sphere_x.setColor((1, 0, 0, 1))
        node_path_sphere_x.setPos(1, 0, 0)
        sphere_y = create_sphere_node("y", 12, 12)
        self.rdr_scene.attachNewNode(sphere_y)
        node_path_sphere_y = NodePath(sphere_y)
        node_path_sphere_y.setColor((0, 1, 0, 1))
        node_path_sphere_y.setPos(0, 1, 0)
        sphere_z = create_sphere_node("z", 12, 12)
        self.rdr_scene.attachNewNode(sphere_z)
        node_path_sphere_z = NodePath(sphere_z)
        node_path_sphere_z.setColor((0, 0, 1, 1))
        node_path_sphere_z.setPos(0, 0, 1)
        node_path_sphere_o.setScale(0.2)
        node_path_sphere_x.setScale(0.2)
        node_path_sphere_y.setScale(0.2)
        node_path_sphere_z.setScale(0.2)





class QtInterface(DirectObject):
    pass


class CMDInterface(DirectObject):
    def __init__(self, console:Console) -> None:
        super().__init__()
        # self.queue = Queue()
        self.thread = Thread(
            target=self.listen_input
        )
        self.console = console
        self.lock = Lock()
        # TODO: a boolean flag to indicate whether the thread
        # is started
        self.prompt = "(game prompt)"
        self.is_end=False
        # self.console.command_dict.update({
            # "quit": (self.end_interface, "end game")
        # })
        # self.accept(Events.InterfaceEndEvent, self.end_interface)
        self.console._end_interface = self.end_interface

    # @property
    # def messageq(self):
        # # TODO: self.buffer
        # return self.console.messageq

    def end_interface(self):
        print("end interface")
        self.is_end = True

    # def send_messages(self):
        # while not self.messageq.empty():
            # message = self.messageq.get()
            # print(message)
            # Task.messenger.send(message)
    def print_output(self):
        while not self.console.out_buffer.empty():
            print(self.console.out_buffer.get())

    def print_log(self):
        while not self.console.log_buffer.empty():
            print(self.console.log_buffer.get())

    def listen_input(self):
        while not self.is_end:
            self.lock.acquire()
            prompt = self.prompt
            self.lock.release()
            input_str = input(prompt)
            self.lock.acquire()
            try:
                Console.parse(self.console, input_str)
                self.print_output()
                self.print_log()
            except Exception as e:
                print(e)
            self.lock.release()
            # self.send_messages()

    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()

    def set_prompt(self, s):
        self.lock.acquire()
        self.prompt = s
        self.lock.release()

if __name__ == "__main__":
    from ui.abstract_ui import InterfacePlaceHolder
    import builtins
    import traceback
    interface = InterfacePlaceHolder()
    try:
        with PhyscRoom(25, 25, 25) as app:
            console = PhyscRoomConsole(showbase=app)
            interface = CMDInterface(console=console)
            interface.start()
            # start a thread of app
            app.run()
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    finally:
        if hasattr(builtins, 'base'):
            builtins.base.destroy()
        interface.join()
