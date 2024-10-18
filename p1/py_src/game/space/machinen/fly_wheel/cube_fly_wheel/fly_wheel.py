from panda3d_game.game_object import  PhysicsGameObject

from panda3d.core import (
    LPoint3f, VBase3,
    TransformState
)
from panda3d.bullet import (
    BulletHingeConstraint
)
from game.space.machinen.fly_wheel.cube_fly_wheel.wheel import *
from game.space.machinen.fly_wheel.cube_fly_wheel.frame import *
class FlyWheel(PhysicsGameObject):

    def setLinearVelocity(self, v):
        for c in self.children:
            c.rigid_node.setLinearVelocity(v)
    # rigid_body.setAngularVelocity(angular_velocity)
    @property
    def mainPath(self):
        return self.frame.mainPath

    def reparentTo(self, other):
        for child in self.children:
            child.reparentTo(other)
        # self.mainPath.reparentTo(other)

    def toBulletWorld(self, world):
        for child in self.children:
            child.toBulletWorld(world)
        # self.mainPath
        for constraint in self.constraints:
            world.attachConstraint(constraint)

    def setActive(self,state):
        for c in self.children:
            c.rigid_node.setActive(state)
            print(c, c.rigid_node.isActive())

    
    def __init__(
        self,
        length,
        frame_width,
        frame_mass,
        single_wheel_mass,
        name:str,
        debug=False,
    ):
        PhysicsGameObject.__init__(self)
        self.length = float(length)
        self.frame_width = float(frame_width)
        self.frame_mass = float(frame_mass)
        self.single_wheel_mass = float(single_wheel_mass)
        self.wheel_radius = float(length / 2 - frame_width-0.1)
        self.name = "FlyWheel.{}".format(name)
        self.frame = FlyWheelFrame(
            name=self.name,
            edge_length=self.length,
            edge_width=self.frame_width,
            mass=self.single_wheel_mass
        )
        bearings_loc = self.frame.rolling_bearings()
        self.bearing_x = WheelPair(
            self.wheel_radius,
            self.frame_width,
            self.single_wheel_mass,
            [bearings_loc["x+"], bearings_loc["x-"]],
            f"{self.name}.x"
        )
        self.bearing_x.setColor((1,0,0,1))
        self.bearing_y = WheelPair(
            self.wheel_radius,
            self.frame_width,
            self.single_wheel_mass,
            [bearings_loc["y+"], bearings_loc["y-"]],
            f"{self.name}.y"
        )
        self.bearing_z = WheelPair(
            self.wheel_radius,
            self.frame_width,
            self.single_wheel_mass,
            [bearings_loc["z+"], bearings_loc["z-"]],
            f"{self.name}.z"
        )
        self.children = [
            self.frame, 
            self.bearing_x,
            self.bearing_y, 
            self.bearing_z
        ]
        # self.bearing_x.reparentTo(self.mainPath)
        # self.bearing_y.reparentTo(self.mainPath)
        # self.bearing_z.reparentTo(self.mainPath) #FIXME
        self.hinge_x = BulletHingeConstraint(
            self.frame.rigid_node, self.bearing_x.rigid_node, 
            LPoint3f(0, 0, 0),LPoint3f(0, 0, 0),
            Vec3(1,0,0),Vec3(1,0,0)
        )
        self.hinge_y = BulletHingeConstraint(
            self.frame.rigid_node, self.bearing_y.rigid_node,
            LPoint3f(0, 0, 0), LPoint3f(0, 0, 0), 
            Vec3(0,1,0), Vec3(0,1,0),
        )
        self.hinge_z = BulletHingeConstraint(
            self.frame.rigid_node, self.bearing_z.rigid_node, 
            LPoint3f(0, 0, 0), LPoint3f(0, 0, 0), 
            Vec3(0,0,1), Vec3(0,0,1),
        )
        self.constraints = [
            self.hinge_x, 
            self.hinge_y, 
            self.hinge_z
        ]
        if debug:
            for c in self.constraints:
                c.setDebugDrawSize(40.0)
        self.rigid_node = self.frame.rigid_node
        self.attachPoint = TransformState.makePos((0,0,0))
        # self._torque = torch.Tensor([0,0,0])

 

    def set_torque(self, torque):
        self._torque = torque
        # joint
    # def apply_torque(self, torque):
    #     self.bearing_x.rigid_node

    def make_torque(self, torque):
        torque_x = torque[0]
        torque_y = torque[1]
        torque_z = torque[2]
        # wheel: reverse torque
        self.bearing_x.rigid_node.applyTorque(VBase3(-torque_x,0,0))
        self.bearing_y.rigid_node.applyTorque(VBase3(0,-torque_y,0))
        self.bearing_z.rigid_node.applyTorque(VBase3(0,0,-torque_z))
        self.frame.rigid_node.applyTorque(VBase3(torque_x,torque_y,torque_z))
        