from typing import List, Union
from panda3d.core import NodePath


class GameObject:
    nodePath: NodePath
    geomNodePath: NodePath
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
