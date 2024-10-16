from panda3d.core import (
    NodePath
)
from panda3d.bullet import (
    BulletRigidBodyNode,
)
from art.basic import *
from panda3d_game.game_object import  PhysicsGameObject
from util.bullet_geometry import *

class WheelPair(PhysicsGameObject):
    def setColor(self, rgba):
        self.wheel1_np.setColor(rgba)
        self.wheel2_np.setColor(rgba)

    # @property
    # def mainPath(self):
    #     return self.rigid_np
    def __init__(
        self, 
        radius:float, 
        thickness:float,
        single_mass:float,
        loc_rolling_bearings, name: str
    ):
        """
        :param radius:
        :param thickness:
        :param loc_rolling_bearings: location and also direction of 2 rolling rears, [(x,y,z), (x,y,z)]
        """
        PhysicsGameObject.__init__(self)
        self.name = "Wheel.{}".format(name)
        self.radius = float(radius)
        self.thickness = float(thickness)
        self.single_mass = float(single_mass)
        self.rigid_node = BulletRigidBodyNode(f'{self.name}.rigid')
        self.rigid_node.setMass(2*self.single_mass)
        self.wheel1 = create_cylinder_node(
            name=f"{self.name}.1",
            radius=self.radius,
            height=self.thickness,
            lon_res=8,
        )
        self.wheel2 = create_cylinder_node(
            name=f"{self.name}.2",
            radius=self.radius,
            height=self.thickness,
            lon_res=8,
        )
        cylinder_geom = create_cylinder(
            name="tmp",
            radius=self.radius,
            height=self.thickness,
            lon_res=8,
            with_bot=False,
            with_top=False
        )
        # cylinder_shape = BulletCylinderShape(radius=self.radius, height=self.thickness,up=1)
        # cylinder_shape = getCylinderShape(radius=self.radius, height=self.thickness, lon_res=8)
        self.wheel1_np = NodePath(self.wheel1)
        # print(self.wheel1_np.getGeom(0))
        self.wheel2_np = NodePath(self.wheel2)
        self.wheel1_np.lookAt(*(loc_rolling_bearings[0]))
        self.wheel1_np.setPos(*(loc_rolling_bearings[0]))
        self.wheel2_np.lookAt(*(loc_rolling_bearings[1]))
        self.wheel2_np.setPos(*(loc_rolling_bearings[1]))
        convec_hull_wheel1 = create_convex_hull_shape_tr(
            geoms=[cylinder_geom],
            transforms=[self.wheel1_np.getTransform().getMat()]
        )
        convec_hull_wheel2 = create_convex_hull_shape_tr(
            # geoms=[self.wheel2.getGeom(0)],
            geoms=[cylinder_geom],
            transforms=[self.wheel2_np.getTransform().getMat()]
        )
        self.rigid_node.addShape(convec_hull_wheel1)
        self.rigid_node.addShape(convec_hull_wheel2)
        self.rigid_np = NodePath(self.rigid_node)
        self.wheel1_np.reparent_to(self.rigid_np)
        self.wheel2_np.reparent_to(self.rigid_np)
        self.rigid_node.setLinearSleepThreshold(0)
        self.rigid_node.setAngularSleepThreshold(0)
        self.rigid_node.setFriction(0)