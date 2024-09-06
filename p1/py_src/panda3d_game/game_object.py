from typing import List, Union
from panda3d.core import NodePath, LODNode
from util.log import Loggable


class GameObject(Loggable):
    nodePath: NodePath
    geomNodePath: NodePath # FIXME: different NodePath for different resolution
    childrenObjects: List["GameObject"]
    parent: Union["GameObject", NodePath]

    def add_child(self, other: Union["GameObject", NodePath]):
        if isinstance(other, GameObject):
            self.childrenObjects.append(other)
            other.nodePath.reparentTo(self.nodePath)
        elif isinstance(other, NodePath):
            other.nodePath.reparentTo(self.nodePath)
        else:
            raise NotImplementedError

    def reparentTo(self, other: Union["GameObject", NodePath]):
        if isinstance(other, GameObject):
            other.add_child(self)
            self.parent = other
        elif isinstance(other, NodePath):
            self.nodePath.reparentTo(other)
            self.parent = other
        else:
            raise NotImplementedError


    def setPos(self, pos):
        pass

    def rotate(self, mat):
        # TODO: use matrix for rotation, torch.Tensor
        pass

    def setScale(self, scale):
        pass

    def lod(self, dist) -> LODNode:
        pass


class ControlledObject(GameObject):
    def register_controller(self, controller):
        self.controller = controller
        # TODO: T typing
        pass

