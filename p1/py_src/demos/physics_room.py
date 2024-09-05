# TODO: a room with walls
# a camera that can fly
# from panda3d.core import PointLight, DirectionalLight
from panda3d.bullet import BulletWorld
from util.app import ControlShowBase
from util.log import Loggable
from direct.task import Task
from geom.basic import create_cube_node, create_sphere_node, uv_curve_surface, create_colored_cube_node
from panda3d.core import (
    NodePath,
    PointLight,
    DirectionalLight,
    CardMaker,
    Texture,
    CardMaker,
    Point2
)
from direct.showbase import DirectObject
from game.game_object import GameObject

from util.texture import (
    create_color_checkerboard,
    np2texture
)
from typing import Set, List, Dict, Callable
# import gizeh as gz
import sympy
import torch
from torch import Tensor


def make_wall_texture(
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


class PhyscRoom(ControlShowBase):
    
    def __init__(self, xb: int, yb: int, zb: int):
        super().__init__()
        self.name = "Physics Room"
        self.bullet_world = BulletWorld()
        self.paused = True
        # for controlledShowBase
        # self.display_camera = self.
        self.accept('p', self.pause_switch)
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
        
        # 每帧更新摄像机
        self.taskMgr.add(self.update, 'updateWorld')
        # 保存鼠标的初始位置
        self.prev_mouse_x = 0
        self.prev_mouse_y = 0

    def pause_switch(self):
        self.paused = not self.paused
        self.log("paused:{}".format(self.paused))
        return self.paused

    def update(self, task):  # FIXME: decorator
        if not self.paused:
            dt = globalClock.get_dt()
            self.bullet_world.do_physics(dt)
        return task.cont


if __name__ == "__main__":
    import builtins
    import traceback
    try:
        with PhyscRoom(25, 25, 25) as app:
            app.run()
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    finally:
        if hasattr(builtins, 'base'):
            builtins.base.destroy()
