from typing import List, Union
from panda3d.core import NodePath, LODNode,Vec3
from panda3d.core import Point3, LVector3f, Vec3

from util.log import Loggable
from panda3d.bullet import (
    BulletWorld,
    BulletRigidBodyNode,
)

class GameObject(Loggable):
    geomNodePath: NodePath # FIXME: different NodePath for different resolution
    childrenObjects: List["GameObject"]
    parent: Union["GameObject", NodePath]

    def add_child(self, other: Union["GameObject", NodePath]):
        pass
        # if isinstance(other, GameObject):
            # self.childrenObjects.append(other)
            # other.nodePath.reparentTo(self.nodePath)
        # elif isinstance(other, NodePath):
            # other.nodePath.reparentTo(self.nodePath)
        # else:
            # raise NotImplementedError

    def reparentTo(self, other: Union["GameObject", NodePath]):
        if isinstance(other, GameObject):
            other.add_child(self)
            self.parent = other
        elif isinstance(other, NodePath):
            self.mainPath.reparentTo(other)
            self.parent = other
        else:
            raise NotImplementedError

    @property
    def mainPath(self) -> NodePath:
        pass


    def setPos(self, pos):
        pass

    def setX(self, *args):
        pass

    def setY(self, *args):
        pass

    def setZ(self, *args):
        pass

    def set_linear_velocity(self,v:Vec3):
        # self.rigid_body_node.set_linear_velocity(v)
        pass

    def rotate(self, mat):
        # TODO: use matrix for rotation, torch.Tensor
        pass

    def setScale(self, scale):
        pass

    def lod(self, dist) -> LODNode:
        pass

    def getPos(self, other=None):
        if other is None:
            return self.mainPath.getPos()
        elif isinstance(other, NodePath):
            return self.mainPath.getPos(other)
        else:
            return self.mainPath.getPos(other.mainPath)



class PhysicsGameObject(GameObject):
    rigid_body_node: BulletRigidBodyNode
    rigid_body_np: NodePath
    game_mass:float


    def toBulletWorld(self, world:BulletWorld):
        raise NotImplementedError

    @property
    def mainPath(self) -> NodePath:
        return self.rigid_body_np

    def apply_force(self, force, pos):
        self.rigid_body_node.apply_force(LVector3f(*force), LVector3f(*pos))

    def set_linear_velocity(self,v:Vec3):
        self.rigid_body_node.set_linear_velocity(v)

    def setZ(self,*args):
        self.rigid_body_np.setZ(*args)

    def setPos(self, *args):
        # super().setPos(self,*args)
        self.rigid_body_np.setPos(*args)







class ControlledObject(GameObject):
    def register_controller(self, controller):
        self.controller = controller
        # TODO: T typing
        pass


