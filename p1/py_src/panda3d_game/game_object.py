# -*- coding: utf-8-*-
# TODO: save and load object with json

from typing import List, Union, Callable
from panda3d.core import (
    NodePath, LODNode,Vec3,
    Point3, LVector3f,
    TransformState
)

from util.log import Loggable
from panda3d.bullet import (
    BulletWorld,
    BulletRigidBodyNode,
)

class GameObject(Loggable):
    geomNodePath: NodePath # FIXME: different NodePath for different resolution
    # childrenObjects: List["GameObject"]
    parent: Union["GameObject", NodePath]

    tasks: List[Callable]
    def xform(self, xform):
        def xform_recur(*args, **kwargs):
            children_rel_trans = {
                c: c.mainPath.getMat(self.mainPath)
                for c in self.children
            }
            ret = xform(*args,**kwargs)
            for c in self.children:
                rel_trans = TransformState.makeMat(children_rel_trans[c])
                c.setTransform(self.mainPath, rel_trans)
            return ret
        return xform_recur

    def __init__(self):
        Loggable.__init__(self)
        if not hasattr(self, "children"):
            self.children = []

    def setTransform(self, *args, **kwargs):
        # TODO: decorator
        @self.xform
        def inner():
            self.mainPath.setTransform(*args, **kwargs)
        inner()

    def setPos(self,*args, **kwargs):
        @self.xform
        def inner():
            self.mainPath.setPos(*args,**kwargs)
        inner()

    #TODO: set Mat

    def __hash__(self):
        return id(self)

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

def sync_pos(nodepath):
    transform = nodepath.getTransform()
    nodepath.node().setTransform(transform)

class PhysicsGameObject(GameObject):
    rigid_node: BulletRigidBodyNode
    rigid_np: NodePath
    game_mass:float
    constraints:list

    # def findAllRigidNp(self):
    #     rigid_bodies = self.mainPath.findAllMatches('**/+BulletRigidBodyNode')
    #     return rigid_bodies

    # def sync_pos(self):
    #     sync_pos(self.mainPath)
    #     rigid_bodies = self.findAllRigidNp()
    #     for path in rigid_bodies:
    #         sync_pos(path)

    #  TODO: set pos for all physics objects children

    def __init__(self):
        GameObject.__init__(self)
        if not hasattr(self, "isPhysicsGameObjInit"):
            self.constraints = []
            self.isPhysicsGameObjInit = True


    def toBulletWorld(self, bullet_world:BulletWorld):
        bullet_world.attachRigidBody(self.rigid_node)
        for constraint in self.constraints:
            bullet_world.attachConstraint(constraint)
        for c in self.children:
            try:
                c.toBulletWorld(bullet_world)
            except Exception as e:
                self.log(e)

    @property
    def mainPath(self) -> NodePath:
        return self.rigid_np

    def apply_force(self, force, pos):
        self.rigid_node.apply_force(LVector3f(*force), LVector3f(*pos))

    def set_linear_velocity(self,v:Vec3):
        self.rigid_node.set_linear_velocity(v)

    def setZ(self,*args):
        self.rigid_np.setZ(*args)





class ControlledObject(GameObject):
    def register_controller(self, controller):
        self.controller = controller
        # TODO: T typing
        pass


