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



from game.space.machinen.shuttle.obj000 import Obj000

class ShipScene(
    StarScene, 
    UniversalGravitySpace, 
    QControl
    # ControlShowBase
):
    def __init__(self, num_iterations=20):
        print(1)
        StarScene.__init__(self)
        print(2)
        unit = {
            "mass" : tonne,
            "length" : 10*meter,
            "time": 1 * second,
            # "force" : sp.Number(1e3) * newton
        }
        G_game = 0.001
        UniversalGravitySpace.__init__(self, unit, G_game, 20, 1/(60*20))
        QControl.__init__(self)
        # self.bullet_world.set_solver_iterations(num_iterations)

       
        self.ship = Obj000(unit=self.unit, name="test")
        
        self.ship.reparentTo(self.rdr_scene)
        self.ship.toBulletWorld(self.bullet_world)
        self.mass = self.ship.flywheel.rigid_node
        self.ship.setPos((0,0,10))
       
        point_light = PointLight('light')
        
        point_light.setColor((1, 1, 1, 1))  # 设置光源颜色 (白色)
        point_light.setShadowCaster(True)
        light_np = self.render.attachNewNode(point_light)
        light_np.setPos(2, 2, 2)
        self.render.setLight(light_np)  # 将光源应用到场景
        
        # point_light.set_sc
        dire_light =DirectionalLight('light')
        dire_light.setDirection((-1,-1,-1))
        dire_light.set_color((1, 1, 1, 1.0)) 
        dire_light.setShadowCaster(True)
        light_dr = render.attachNewNode(dire_light)
        # light_dr.setPos(1, 2, 6)  # 设置光源位置
        
        self.render.setShaderAuto()
        self.render.setLight(light_dr)
        self.startQt()
        # self.ship.toBulletWorld(self.bullet_world)
        # self.shell.toBulletWorld(self.bullet_world)
        # self.planet1.toBulletWorld(self.bullet_world)
        # self.taskMgr.add(self.update_torque_)
        torque = 10000 * 50
        v = 1e10
        self.accept("1", self.add_torque, [torque,0,0])
        self.accept("3", self.add_torque, [0,torque,0])
        self.accept("5", self.add_torque, [0,0,torque])
        self.accept("2", self.add_torque, [-torque,0,0])
        self.accept("4", self.add_torque, [0,-torque,0])
        self.accept("6", self.add_torque, [0,0,-torque])
        # self.accept("1", self.toAngV, [v,0,0])
        # self.accept("3", self.toAngV, [0,v,0])
        # self.accept("5", self.toAngV, [0,0,v])
        # self.accept("2", self.toAngV, [-v,0,0])
        # self.accept("4", self.toAngV, [0,-v,0])
        # self.accept("6", self.toAngV, [0,0,-v])

        debug_node = BulletDebugNode('Debug')
        debug_node.showWireframe(True)
        debug_node.showConstraints(True)
        debug_node.showBoundingBoxes(False)
        debug_node.showNormals(False)
        debug_np = self.rdr_scene.attach_new_node(debug_node)
        self.bullet_world.set_debug_node(debug_node)
        debug_np.show()
    # def update_torque_(self, task):
    #     # self.ship.flywheel.apply_torque_on_axis()
    #     self.ship.shell.rigid_node.applyTorque((1,0,0))
    #     return task.cont

    def add_torque(self, x=0, y=0, z=0):
        # print(x,y,z)
        self.ship.flywheel.make_torque((x,y,z))

    def toAngV(self, x=0,y=0,z=0):
        self.ship.flywheel.toAngV((x,y,z))

class ShipView(RawQtGUI):
    def get_game(self):
        return ShipScene()

    def get_console(self):
        return PhyscRoomConsole(showbase=self.panda3d)
        
if __name__ == '__main__':
    torch.set_printoptions(precision=16, sci_mode=False)
    import sys
    app = QApplication(sys.argv)
    window = ShipView()
    window.show()
    sys.exit(app.exec_())   
