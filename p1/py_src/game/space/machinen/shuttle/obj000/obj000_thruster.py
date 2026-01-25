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


from game.space.machinen.thruster.thruster import MagicThruster #FIXME

class Obj000_ThrusterSet(PhysicsGameObject):
    #TODO: enum gears
    def reparentTo(self, other):
        # if other is game object: TODO
        self.mainPath.reparentTo(other)
        for c in self.children:
            c.reparentTo(other)

    def __init__(self, name, unit, is_up=False):
        PhysicsGameObject.__init__(self)
        # scale_factor = float(scale_factor)
        self.name = f"ThruS.{name}"
        self.unit = unit
        self.ridge_mass = 10 * tonne
        self.thruster_length = 50 * meter
        self.thruster_radius = 20 * meter
        self.thruster_rigid_length = 10 * meter
        scale_factor = float(1*meter / unit["length"])
        
        # self.tasks = []
        
        ridge_y = torch.arange(0,40+5,step=5).float()
        ridge_z = 0.03 * (ridge_y ** 2) - 20 
        ridge_y = ridge_y + 20
        ridge_y = torch.hstack([-ridge_y.flip(dims=[0]), ridge_y]) # mirror effect
        ridge_z = torch.hstack([ridge_z.flip(dims=[0]), ridge_z])
        ridge_x_front = torch.ones_like(ridge_y) * 20
        ridge_x_back  = torch.ones_like(ridge_y) * -20
        # FIXME: rename
        if is_up:
            ridge_z = - ridge_z # FIXME: flip
        _1 = torch.concat([ridge_x_front.unsqueeze(-1),ridge_y.unsqueeze(-1),ridge_z.unsqueeze(-1)],dim=-1)
        _2 = torch.concat([ridge_x_back.unsqueeze(-1),ridge_y.unsqueeze(-1),ridge_z.unsqueeze(-1)],dim=-1)
        y_mean = torch.mean(ridge_y).item()
        z_mean = torch.mean(ridge_z).item()
        frontend = torch.ones_like(_1) * torch.Tensor([20, y_mean,z_mean])
        backend  = torch.ones_like(_2) * torch.Tensor([-20, y_mean, z_mean])
        # [4,18,3 ]
        ridge_xyz = torch.concat([frontend.unsqueeze(0), _1.unsqueeze(0), _2.unsqueeze(0), backend.unsqueeze(0)],dim=0)
        ridge_xyz = ridge_xyz * scale_factor
        self.geom_node = GeomNode(self.name)
        self.ridge_geom = uv_curve_surface(
            name = f"rg.{self.name}",
            coord_mat=ridge_xyz,
            is_u_loop=False,
            is_v_loop=True,
        )
        self.geom_node.addGeom(self.ridge_geom)
        self.ridge_np = NodePath(self.geom_node)
        # FIXME: use vertex instead of geom 
        convec_hull_shape = create_convex_hull_shape(
            geoms=[self.ridge_geom]
        )
        self.rigid_node = BulletRigidBodyNode(f"{self.name}.rigid")
        self.rigid_node.setMass(float(self.ridge_mass / unit["mass"]))
        self.rigid_node.addShape(convec_hull_shape)
        self.rigid_np = NodePath(self.rigid_node)
        self.ridge_np.reparentTo(self.rigid_np)
        self.rigid_node.setLinearSleepThreshold(0)
        self.rigid_node.setAngularSleepThreshold(0)

        if is_up:
            self.thruster_loc = {
                "up":(0,0,20),
                "forward":(20,0,0),
                "backward":(-20,0,0)
            }
        else:
            self.thruster_loc = {
                "down":(0,0,-20),
                "forward":(20,0,0),
                "backward":(-20,0,0)
            }
        self.thrusters_d = {}
        for loc_key, loc in self.thruster_loc.items():
            loc_scaled = (
                loc[0]*scale_factor,
                loc[1]*scale_factor,
                loc[2]*scale_factor
            )
            t = MagicThruster(
                name=f"{self.name}.{loc_key}",
                radius=self.thruster_radius / self.unit["length"],
                length=self.thruster_length / self.unit["length"],
                rigid_length=self.thruster_rigid_length / self.unit["length"],
                mount_shift=20 * meter/self.unit["length"],
                direction=loc_scaled
            )
            self.thrusters_d[loc_key] = t
            t.setPos(loc_scaled)
            
        self.children = list(self.thrusters_d.values())
        self.shellAttachPoint = TransformState.makePos((0,0,0))
        # for loc_key, loc in self.thruster_loc.items():
        #     print(loc, type(loc))
        #     t = TransformState.makePos(loc)
        self.thrusterAttachPoints = {
            loc_key: TransformState.makePos((0,0,0))
            for loc_key, loc in self.thruster_loc.items()
        }
        self.thrusterConstraints = {
            loc_key : FixedConstraint(
                self.thrusters_d[loc_key].rigid_node, self.rigid_node, 
                self.thrusters_d[loc_key].attachPoint, self.thrusterAttachPoints[loc_key], True
            # LPoint3f(0,0,0), # LPoint3f(0,0,0)
            )
            for loc_key in self.thruster_loc.keys()
        }
        self.constraints = self.thrusterConstraints.values()

        # attach points: two attach points FIXME
            
    @property
    def thrusters(self) -> List[Thruster]:
        return self.children
    pass


