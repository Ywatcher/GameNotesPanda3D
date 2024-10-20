# -*- coding: utf-8-*-

# import datetime
from datetime import datetime
from queue import Queue as PyQueue
from typing import Dict, Union, List
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.showbase.InputStateGlobal import inputState
from panda3d.bullet import BulletWorld
from panda3d.core import (
    WindowProperties,
    KeyboardButton,
    NodePath,
)
import sympy as sp
import torch
from torch import Tensor
from torch.nn import functional as F
from sympy.physics.units import (
    kilometer, meter,centimeter,
    gram, kilogram, tonne,
    newton, second
)
from panda3d_game.camera_controller import CameraController, PlayerCamController
from panda3d_game.controller import PlayerController
from panda3d_game.app.app_ import ContextShowBase
from panda3d_game.game_object import GameObject, PhysicsGameObject

from game.events import Events
from util.physics import autocomplete_units, getG
from util.math import safe_reciprocal
from util.log import Loggable

class PhysicsShowBase(ContextShowBase):
    def __init__(
        self,
        unit:dict={
            "mass" : tonne,
            "length" : 100*meter,
            "time": 1 * second,
            # "force" : sp.Number(1e3) * newton
        },
        max_sub_steps=1,
        time_step=1.0/60.0
    ):
        if not hasattr(self, "isPhysicsShowBaseInit"):
            ContextShowBase.__init__(self)
            self.isPhysicsShowBaseInit = True
            self.unit = unit
            autocomplete_units(self.unit)
            if not hasattr(self, 'bullet_world'):
                self.bullet_world = BulletWorld()
            self.paused = True
            # objects to access
            self.objects: Dict[str, Union[GameObject, NodePath]] = {}
            # update physisc world
            self.taskMgr.add(self.update, 'updateWorld')
            self.maxSubSteps =max_sub_steps
            self.timeStep = time_step

    def pause_switch(self):
        self.paused = not self.paused
        self.log("paused:{}".format(self.paused), "log")
        return self.paused

    def update(self, task):  # FIXME: decorator
        if not self.paused:
            dt = globalClock.get_dt()
            self.bullet_world.doPhysics(dt, self.maxSubSteps, self.timeStep)
        return task.cont


class UniversalGravitySpace(PhysicsShowBase):
    def setGGame(self, G_game:float):
        self.G_game = float(G_game)

    def set_G_game(self, G_game):
        self.setGGame(G_game)

    def __init__(
        self,
        unit:dict,
        G_val: Union[float, sp.Expr],
        max_sub_steps=1,
        time_step = 1.0/60.0
    ):
        if not hasattr(self, "isUniversalGravitySpaceInit"):
            PhysicsShowBase.__init__(self,unit,max_sub_steps,time_step)
            self.isUniversalGravitySpaceInit = True
            self.bullet_world.setGravity((0,0,0))
            if isinstance(G_val, sp.Expr):
                self.G_real = G_val
                self.G_game = getG(self.unit, G_val=G_val)
            else:
                try:
                    self.G_game = float(G_val)
                except Exception as e:
                    raise e
            self.G_game_tensor = torch.Tensor([self.G_game])
            if not hasattr(self, 'gravitational_bodies'):
                # TODO: gravitation in groups
                self.gravitational_bodies = []

    @property
    def masses(self):
        if hasattr(self, "_masses"):
            return self._masses
        else:
            self._masses =  self.get_mass(self.gravitational_bodies)
            return self._masses


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
        """
        :return: n by d tensor,
            n be number of nodepaths,
            d be 3
        """
        pos = torch.Tensor([
            n.getPos()
            for n in node_paths
        ])
        return pos

    @staticmethod
    def get_node_dist(node_paths:List[NodePath]) -> Tensor:
        """
        get vector distance between each two nodes in the lists
        be aware, this gives the pos of each i in
            the COOORDINATE of each j,
            if j is rotated then the axes are rotated
        :node_paths: n nodes
        :return: nxnx3 tensor for vector distance
        """
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
    def get_mass(objs:List[PhysicsGameObject]) -> torch.Tensor:
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
        if not self.paused and len(self.gravitational_bodies)>0:
            self.apply_gravitational_force(task)
        return super().update(task)






