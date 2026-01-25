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



class Obj000_shell(PhysicsGameObject):
    def setScale(self, scale):
        # FIXME
        # self.geom_np.setScale(scale)
        self.rigid_np.setScale(scale)

    def setColor(self, r,g,b,a):
        self.geom_np.setColor(r,g,b,a)

    def setTexture(self,t):
        self.geom_np.set_texture(t)
        
    def __init__(self, r1, r2, a, frame_thickness, keel_thickness, name, mass=1):
        # print(r1, type(r1),float(r1))
        # FIXME: use sympy
        r1 = float(r1)
        r2 = float(r2)
        a = float(a)
        mass = float(mass)
        frame_thickness = float(frame_thickness)
        keel_thickness = float(keel_thickness)
        super().__init__()
        assert r2 >= r1
        self.r1 = r1
        self.r2 = r2
        self.a = a
        self.mass = mass
        self.frame_thickness = frame_thickness
        self.keel_thickness = keel_thickness
        self.name = "Shell.{}".format(name)
        self.geom_node = GeomNode(self.name)
        self.rigid_node = BulletRigidBodyNode(f"{self.name}.rigid")
        # 2 paraboloids in column coord
        self.n_step_shell = 6
        theta = torch.arange(start=0, end=2 * np.pi, step=np.pi/self.n_step_shell)
        step = (r2 - r1) / 6
        rho = torch.arange(start=r1, end=r2 + step, step=step)
        z_2_shift = self.a * self.r2 ** 2
        self.geom_c1 = uv_curve_surface_lambda(
            f"{self.name}.1",
            u=theta,v=rho,
            is_u_loop=True, is_v_loop=False,
            x_uv=lambda _theta, _rho: a * _rho ** 2 - z_2_shift,
            y_uv=lambda _theta, _rho: _rho * np.cos(_theta),
            z_uv=lambda _theta, _rho: _rho * np.sin(-_theta),
            # FIXME geom node
        )
        self.geom_c2 = uv_curve_surface_lambda(
            f"{self.name}.2",
            u=theta,v=rho,
            is_u_loop=True, is_v_loop=False,
            x_uv=lambda _theta, _rho: -  a * _rho ** 2 + z_2_shift,
            y_uv=lambda _theta, _rho: _rho * np.cos(_theta),
            z_uv=lambda _theta, _rho: _rho * np.sin(_theta),
            # FIXME geom node
        )
        self.geom_node.addGeom(self.geom_c1)
        self.geom_node.addGeom(self.geom_c2)
        self.geom_np = NodePath(self.geom_node)
        # convec_hull_shape = create_convex_hull_shape(
        #     geoms=[self.geom_c1,self.geom_c2]
        # )
        self.n_step_frame = 8
        step = (r2 - r1) / self.n_step_frame
        rho = torch.arange(start=r1, end=r2+step, step=step)[1:-1]
        z_2_shift = a * r2 ** 2
        pos_x = a * rho ** 2 - z_2_shift
        self.rigid_node.setMass(self.mass)
        for i in range(len(rho)):
            pos_xi = pos_x[i]
            ri = rho[i]
            shape = BulletCylinderShape(radius=ri, height=self.frame_thickness, up=0)
            self.rigid_node.addShape(shape, TransformState.makePos((pos_xi,0,0)))
            self.rigid_node.addShape(shape, TransformState.makePos((-pos_xi,0,0)))
       
        self.rigid_node.setRestitution(0)
        self.rigid_node.setFriction(0)
        
        self.rigid_np = NodePath(self.rigid_node)
        self.rigid_np.setCollideMask(BitMask32.bit(0))
        self.geom_np.reparentTo(self.rigid_np)
        self.rigid_node.setLinearSleepThreshold(0)
        self.rigid_node.setAngularSleepThreshold(0)
        self.flywheelAttachPoint = TransformState.makePos((0,0,0))
    # def reparentTo