# -*- coding: utf-8-*-


# a camera that can fly
# from panda3d.core import PointLight, DirectionalLight
import os
from typing import List,Set, List, Dict,Callable
from collections import OrderedDict
from abc import ABC
import numpy as np
import torch
from torch import Tensor
from torch.nn import functional as F
from sympy.physics.units import (
    kilometer, meter,centimeter,
    gram, kilogram, tonne,
    newton, second
)

from panda3d.core import (
    NodePath,
    WindowProperties,
    Vec3,
    TextNode,
    PNMImage, Texture,
    CardMaker,Point2,
    NodePath, Camera, PerspectiveLens,
    Point3, LVector3f
)
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from direct.showbase import DirectObject
from panda3d.bullet import (
    BulletWorld,
    BulletBoxShape,
    BulletPlaneShape,
    BulletRigidBodyNode, BulletSphereShape
)

from panda3d_game.app import ControlShowBase, ContextShowBase
from panda3d_game.game_object import GameObject, PhysicsGameObject
from panda3d_game.controller import PlayerController

# controller
# player controller
# agent controller

from art.basic import (
    create_cube_node, create_sphere_node,
    uv_curve_surface, create_colored_cube_node
)
from demos.physics_room import (
    PhyscRoom, PhyscRoomConsole, CMDInterface
)

from util.maths import one,safe_reciprocal
from util.physics import autocomplete_units, G_val, getG
from util.repo import res_root
tmoon = Texture()
tmoon.read(os.path.join(res_root, "moon.jpeg"))
tmoon.setWrapU(Texture.WM_repeat)
tmoon.setWrapV(Texture.WM_repeat)



class MassedBall(PhysicsGameObject): # not yet inherent GameObject
    def __init__(
        self,
        name,
        radius,
        mass,
        units:dict
        # lat_res,
        # lon_res,
        # geom_type
        # TODO: texture
    ):
        PhysicsGameObject.__init__(self)
        # super().__init__(name)
        self.worlds = []
        self.radius = radius
        self.mass = mass
        self.units = units
        # print(radius / units["length"])
        self.game_radius:float = (radius / units["length"]).simplify().evalf()
        self.game_mass: float = (mass / units["mass"]).simplify().evalf()
        # create geom
        self.geom_node = create_sphere_node(name, lat_res=24,lon_res=24)
        self.geom_np = NodePath(self.geom_node)
        # print(self.game_radius)
        self.geom_np.setScale(self.game_radius)
        # create rigid body
        self.rigid_node = BulletRigidBodyNode("SphrRg."+str(name))
        sphere_shape = BulletSphereShape(self.game_radius)
        self.rigid_node.add_shape(sphere_shape)
        self.rigid_node.set_mass(self.game_mass)
        self.rigid_np = NodePath(self.rigid_node)
        # bind geom to rigid body
        # self.rigid_np.attachNewNode(self.geom_node)
        self.geom_np.reparent_to(self.rigid_np)
        # todo: add collison

    def toBulletWorld(self, world:BulletWorld):
        self.worlds.append(world)
        world.attach_rigid_body(self.rigid_node)
        # if there is contraint, attach constraint

    def set_texture(self, t):
        self.geom_np.set_texture(t)

    def set_tex_scale(self, t):
        self.geom_np.set_tex_scale(t)

class MultiRegionApp(PhyscRoom):

    def add_text(self, label:str, content:str):
        next_i = len(self.pane_texts)
        # FIXME
        pos_x = self.default_pos_text[0]
        pos_y = self.default_pos_text[1] - .1*next_i
        new_text = OnscreenText(
            text=content,
            pos = (pos_x, pos_y),
            scale = .05,
            fg=(0,0,0,1), # colour inside
            shadow=(1,1,1,1), # colour outline
            # shadow= # colour of shadow
            align=TextNode.ALeft,
            mayChange=True
        )
        self.pane_texts.update({label:new_text})

    def update_text(self, task):
        cam_pos = self.camera.getPos()
        self.pane_texts["cam_pos"].setText(
            # FIXME: let user set this format
            "CamPos:(x:{:.2f},y:{:.2f},z:{:.2f})".format(
                *cam_pos
            )
        )
        cam_forward = self.camera.getQuat(self.render).getForward()
        self.pane_texts["cam_vec"].setText(
            # FIXME: let user set this format
            "Looking at: ({:.2f},{:.2f},{:.2f})".format(
                *cam_forward
            )
        )
        # print(cam_pos)
        return Task.cont


    def __init__(self, xb:int=25, yb:int=25 , zb:int=25):
        ContextShowBase.__init__(self)
        super().__init__(xb,yb,zb)

        # super().__init__()
        self.default_pos_text = (-.8, .9)
        self.pane_texts = OrderedDict() # FIXME
        self.add_text(
            "cam_pos", "CamPos:(x:-,y:-,z:-)"
        )
        self.add_text(
            "cam_vec", "Looking at: (-,-,-)"
        )
        self.taskMgr.add(self.update_text, "update text")

class PhysicsRoomBalls(MultiRegionApp):
    def setG(self, G_game):
        self.G_game = float(G_game)

    @property
    def masses(self):
        if hasattr(self, "_masses"):
            return self._masses
        else:
            self._masses =  self.get_mass(self.gravitational_bodies)
            return self._masses
    def __init__(self, xb:int, yb:int , zb:int):
        super().__init__(xb,yb,zb)
        # objects

        self.bullet_world.setGravity((0,0,0)) # no global gravity
        self.unit = {
            "mass" : tonne,
            "length" : 100*meter,
            "time": 1 * second,
            # "force" : sp.Number(1e3) * newton
        }
        autocomplete_units(self.unit)
        # self.G_game = getG(self.unit, G_val=G_val)
        self.G_game = 0.001
        self.G_game_tensor = torch.Tensor([self.G_game])

        self.planet1 = MassedBall(
            name="planet1",
            radius=100*meter,
            mass=1e6*tonne,
            units=self.unit
        )
        self.planet1.reparentTo(self.render)
        self.planet2 = MassedBall(
            name="planet2",
            radius=100*meter,
            mass=2e6*tonne,
            units=self.unit
        )
        self.planet2.reparentTo(self.render)
        self.planet2.toBulletWorld(self.bullet_world)


        self.planet1.set_texture(tmoon)
        self.planet2.set_texture(tmoon)
        self.planet2.setZ(4)
        self.planet1.setZ(-4)
        self.planet1.toBulletWorld(self.bullet_world)
        self.gravitational_bodies = [self.planet1, self.planet2]
        self.objects.update({
            "planet1": self.planet1,
            "planet2": self.planet2
        })

    def apply_gravitational_force(self, task):
        # N by N matrix, upper triaglar
        node_poses = self.get_node_poses(self.gravitational_bodies)
        node_dist = node_poses.unsqueeze(0) - node_poses.unsqueeze(1)
        gravity = self.cal_gravity(
            self.masses,
            node_dist,
            sumup=True
        )
        self.batch_apply_force(
            self.gravitational_bodies,
            gravity,
            self.get_node_poses(self.gravitational_bodies)
        )

    @staticmethod
    def get_node_poses(node_paths:List[NodePath]) -> Tensor:
        pos = torch.Tensor([
            n.getPos()
            for n in node_paths
        ])
        return pos

    @staticmethod
    def get_node_dist(node_paths:List[NodePath]) -> Tensor:
        nr_nodes = len(node_paths)
        # FIXME: use vector distance
        # dist ij
        return torch.Tensor([
            [
                node_paths[j].getPos(node_paths[i])
                # if i<j else (0,0,0)
                for j in range(nr_nodes)
            ]
            for i in range(nr_nodes)
        ])

    @staticmethod
    def get_mass(objs:List[MassedBall]) -> torch.Tensor:
        return torch.Tensor([
            o.game_mass for o in objs
        ])

    def cal_gravity(
        self, mass:torch.Tensor,
        dist:torch.Tensor, sumup=False) -> torch.Tensor:
        dist_sq = torch.einsum(
            "mnd -> mn",
            dist ** 2
        )
        dist_sq_rcpr = safe_reciprocal(dist_sq)
        gravity_scalar = torch.einsum(
            "o, n, mn, m -> mn",
            self.G_game_tensor,
            mass, dist_sq_rcpr, mass
        )
        gravity_vector = torch.einsum(
            "mn, mnd -> mnd",
            gravity_scalar,
            F.normalize(dist, dim=2, p=2)
        )
        if sumup:
            return torch.einsum(
                "mnd -> md",
                gravity_vector
            )
        return gravity_vector

    @staticmethod
    def batch_apply_force(bodies, force, pos):
        for i in range(len(bodies)):
            bodies[i].apply_force(
                force[i],
                pos[i]
            )

    def update(self, task):
        if not self.paused:
            self.apply_gravitational_force(task)
        return super().update(task)

class BallRoomConsole(PhyscRoomConsole):
    pass


if __name__ == '__main__':
    import builtins
    import traceback
    try:
        with PhysicsRoomBalls(25,25,25) as app:
            console = PhyscRoomConsole(showbase=app)
            interface = CMDInterface(console=console)
            # TODO: use game manager to restart
            interface.start()
            app.run()
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    finally:
        if hasattr(builtins, 'base'):
            builtins.base.destroy()
