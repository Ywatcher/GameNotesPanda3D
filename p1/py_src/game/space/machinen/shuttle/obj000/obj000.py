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

from game.space.machinen.shuttle.shuttle import Shuttle
from .obj000_shell import Obj000_shell
from .obj000_thruster import Obj000_ThrusterSet


class Obj000(Shuttle, PhysicsGameObject):

    def reparentTo(self, other):
        for child in self.children:
            child.reparentTo(other)

    @property
    def mainPath(self):
        # return self.node_path
        return self.shell.mainPath

    def toBulletWorld(self, bulletWorld):
        # self.shell.toBulletWorld(bulletWorld)
        for c in self.children:
            c.toBulletWorld(bulletWorld)
        for c in self.constraints:
            bulletWorld.attachConstraint(c)
        # self.flywheel.toBulletWorld(bulletWorld) FIXME
        # bulletWorld.attachConstraint(self.fixed_constraint)
    
    def __init__(self, unit, name):
        PhysicsGameObject.__init__(self)
        self.unit = unit
        self.name = name
        # self.node_path = NodePath()
        self.shell_radius_minor = 1 * meter
        self.shell_radius_major = 100 * meter
        self.frame_thickness = 0.1 * meter
        self.keel_thickness = 1 * meter
        self.shell_mass = 1000 * tonne
        self.shell = Obj000_shell(
            r1=self.shell_radius_minor / self.unit["length"],
            r2=self.shell_radius_major / self.unit["length"],
            a=0.02*(self.unit["length"]/meter),
            frame_thickness=self.frame_thickness / self.unit["length"],
            keel_thickness=self.keel_thickness / self.unit["length"],
            mass=self.shell_mass / self.unit["mass"],
            name=self.name
        )
        # self.shell.reparentTo(self.node_path)
        self.fly_wheel_length = 30 * meter 
        self.fly_wheel_width = 3 * meter
        self.thrusterset_shift = 100 * meter
        
        self.flywheel = FlyWheel(
            name=self.name,
            length=self.fly_wheel_length / self.unit["length"],
            frame_width=self.fly_wheel_width / self.unit["length"],
            frame_mass=1,single_wheel_mass=10,
        )
        self.flywheel_constraint = FixedConstraint(
            self.flywheel.rigid_node, self.shell.rigid_node, 
            # Vec3(0, 0, 0)
            self.flywheel.attachPoint, self.shell.flywheelAttachPoint,True
            # LPoint3f(0,0,0), # LPoint3f(0,0,0)
        )
        
        self.thrusterSetTop = Obj000_ThrusterSet(
            name=f"{self.name}.top",
            unit=self.unit,
            is_up=True
        )
        self.thrusterSetTop.setPos(0,0,float(self.thrusterset_shift/self.unit["length"]))
        self.thrAttachPointTop = TransformState.makePos((0,0,float(self.thrusterset_shift/self.unit["length"])))
        # self.thrusters_up.ridge_np.reparentTo(self.mainPath)
        self.thrusterSetBot = Obj000_ThrusterSet(
            name=f"{self.name}.bot",
            unit=self.unit,
            is_up=False
        )
        self.thrusterSetBot.setPos(0,0,-float(self.thrusterset_shift/self.unit["length"]))
        self.thrAttachPointBot = TransformState.makePos((0,0,-float(self.thrusterset_shift/self.unit["length"])))
        self.thr_constraint_top = FixedConstraint(
            self.thrusterSetTop.rigid_node, self.shell.rigid_node,
            self.thrusterSetTop.shellAttachPoint, self.thrAttachPointTop,
            True
        )
        self.thr_constraint_bot = FixedConstraint(
            self.thrusterSetBot.rigid_node, self.shell.rigid_node,
            self.thrusterSetBot.shellAttachPoint, self.thrAttachPointBot,
            True
        )
        self.constraints = [
            self.flywheel_constraint, 
            self.thr_constraint_top,
            self.thr_constraint_bot
        ]
        self.children = [self.shell, self.flywheel, self.thrusterSetTop, self.thrusterSetBot]

    def setFlyWheelTorque(self):
        pass

    def getVelocity(self):
        pass

    def getAngularVelocity(self):
        pass

    def getPos(self):
        pass
        
