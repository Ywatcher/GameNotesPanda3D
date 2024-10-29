from typing import List
import torch
from panda3d.core import (
    Point3, GeomNode, Geom, NodePath
)
from panda3d.bullet import (
    BulletRigidBodyNode, BulletTriangleMeshShape, BulletTriangleMesh
)
from spherical import *


class SphereMeshObject(SphereMesh):
    def __init__(self, R=1, symbolic=False):
        SphereMesh.__init__(self, R, symbolic)
        self.rigid_node = BulletRigidBodyNode()
        # self.geom_node = GeomNode()
        self.mesh = BulletTriangleMesh()
        # self.geom_np = NodePath(self.geom_node)
        self.rigid_np = NodePath(self.rigid_node)
        # self.geom_np.reparentTo(self.rigid_np)

        # TODO: set vert as geom

    def setBulletShape(self):
        for triangle in self.hyperEdgeLevelDict[self.maxLevel]:
            # FIXME: add a new list called leaves
            p0, p1, p2 = tuple(self.verts2point(triangle))
            self.mesh.addTriangle(p0, p1, p2)
        self.rigid_shape = BulletTriangleMeshShape(self.mesh, dynamic=True)
        self.rigid_node.addShape(self.rigid_shape)

    def verts2point(self, verts: List[SphericalVertInfo]):
        idxs = [vert.idx for vert in verts]
        rho = self.getHeight(idxs)
        theta_phi = torch.Tensor([list(vert.tup) for vert in verts])
        # print(theta_phi)
        xyz = sphr2cart_pt(theta_phi[:, 0], theta_phi[:, 1]) * rho
        points = [
            Point3(xyz[i, 0], xyz[i, 1], xyz[i, 2])
            for i in range(len(verts))
        ]
        # print(points)
        return points
