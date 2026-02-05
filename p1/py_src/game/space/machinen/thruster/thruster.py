import torch
import numpy as np
import sympy as sp
from abc import ABC
from typing import List, Dict, Tuple
from panda3d.core import VBase3
from panda3d.core import Quat
from panda3d.core import invert

from panda3d_game.game_object import GameObject, PhysicsGameObject
from panda3d.core import TransformState
# 
from util.geometry import batch_transform, createPosIndicatorNPth
from art.basic import geom_frm_faces, create_cylinder_node, create_cylinder
from panda3d.core import GeomPrimitive
from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GeomEnums, Vec3, LPoint3f
)    
from panda3d.core import GeomNode, NodePath, GeomVertexReader, BitMask32
from art.basic import uv_curve_surface, uv_curve_surface_lambda
from panda3d.bullet import (
    BulletWorld, BulletRigidBodyNode, BulletTriangleMesh, 
    BulletTriangleMeshShape, BulletDebugNode,
      BulletHingeConstraint, BulletGenericConstraint,
    BulletShape, BulletMinkowskiSumShape,BulletCylinderShape,
BulletConvexHullShape
)
from panda3d_game.constraints import FixedConstraint
# class RigidNodePath(NodePath):
#     def setPos(*args,**kwargs):
#         super().setPos(*args,**kwargs)
#         self.node().setTransform(self.getTransform())
from panda3d.bullet import BulletWorld
from util.bullet_geometry import *
from util.geometry import *
from game.space.machinen.fly_wheel.cube_fly_wheel.fly_wheel import FlyWheel
from game.space.machinen.engine.thruster import Thruster
from game.space.machinen.power_supply import ElectricityAppliance
from panda3d.bullet import BulletWorld, BulletRigidBodyNode,  BulletDebugNode
import sys
from demos.starlight_qt import *
import torch
from qpanda3d import QControl # FIXME
from panda3d_game.app import ControlShowBase, UniversalGravitySpace
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletSphereShape, BulletCylinderShape
from panda3d.core import DirectionalLight,  PointLight
from sympy.physics.units import (
    kilometer, meter,centimeter,
    gram, kilogram, tonne,
    newton, second
)
from demos.ball_room import MassedBall,tmoon
from art.basic import create_sphere_node

class MagicThruster(Thruster):
    def __init__(
        self, name, radius, length, rigid_length, direction=None,
        mount_shift=2,
        mass = 1
    ):
        # thrust is magically produced 
        # does not has limit 
        # does not rely on any machanism
        # does not consume fuels
        # used for testing
        super().__init__()
        self._thrust = 0
        self.name = f"Thr.{name}"
        self.radius = float(radius)
        self.length = float(length)
        self.rigid_length = float(rigid_length)
        self.mount_shift = float(mount_shift)
        self.mass = float(mass)
        if direction is None:
            self.direction_init = (1,0,0)
        else:
            direction_sum = abs(sum(direction))
            self.direction_init = (
                direction[0]/direction_sum, 
                direction[1]/direction_sum,
                direction[2]/direction_sum
            )  # todo: setter
        
        self.geom = create_cylinder_node(
            radius=self.radius, height=self.length, 
            name=self.name, lon_res=8
        )
        self.geom_np = NodePath(self.geom)
        self.geom_np.lookAt(Vec3(self.direction_init))
        self.rigid_node = BulletRigidBodyNode(self.name)
        self.rigid_node.setMass(self.mass)
        # TODO: create cylinder shape
        # TODO: add cylinder shape with transformed 
        cylindershape = BulletCylinderShape(
            radius=self.radius, height=self.rigid_length, 
            up=1
        )
        shape_transform_lookAt = makeLookAt(Vec3(self.direction_init))
        rigid_shift = self.length - self.rigid_length/2
        shape_transform_pos = TransformState.makePos((
            self.direction_init[0] * rigid_shift,
            self.direction_init[1] * rigid_shift,
            self.direction_init[2] * rigid_shift
        ))
        # shape_transform = shape_transform_lookAt.compose(shape_transform_pos)                                     
        shape_transform = shape_transform_pos.compose(shape_transform_lookAt)
        self.rigid_node.addShape(cylindershape, shape_transform)
        self.rigid_np = NodePath(self.rigid_node)
        self.geom_np.reparentTo(self.rigid_np)
        self.attachPoint = TransformState.makePos((
            self.direction_init[0] * -self.mount_shift,
            self.direction_init[1] * -self.mount_shift,
            self.direction_init[2] * -self.mount_shift,
        ))
        # self.attachPoint = self.geom_np.getTransform()
        self.rigid_node.setLinearSleepThreshold(0)
        self.rigid_node.setAngularSleepThreshold(0)

    @property
    def thrust_val(self) -> sp.Expr:
        return self._thrust_val

    @property
    def thrust(self) -> torch.Tensor:  # in game scale, without unit 
        return self.thrust_val * self.thrust_dire

    @property
    def thrust_dire(self) -> torch.Tensor:
        # thrust direction
        # fixed for non vector thrust
        return torch.Tensor(self.direction_init)
        
class HallEffectThruster(Thruster, ElectricityAppliance):
    def get_current(self):
        pass
    pass
    
class ThrusterSet(PhysicsGameObject):

    @property
    def thrusters(self) -> List[Thruster]:
        pass
    pass

