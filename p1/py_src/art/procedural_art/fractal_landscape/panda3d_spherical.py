# -*- coding: utf-8-*-

from typing import List
import torch
from panda3d.core import (
    Point3, GeomNode, Geom, NodePath,
    GeomVertexWriter,
    GeomVertexData,
    GeomEnums,
    GeomTriangles
)
from panda3d.bullet import (
    BulletRigidBodyNode, BulletTriangleMeshShape, BulletTriangleMesh
)
from art.procedural_art.fractal_landscape.spherical import *
from util.geometry import *


class SphereMeshObject(SphereMesh):
    def __init__(self, R=1, symbolic=False, name=''):
        SphereMesh.__init__(self, R, symbolic)
        self.name = name
        self.rigid_node = BulletRigidBodyNode()
        self.geom_node = GeomNode(self.name)
        self.mesh = BulletTriangleMesh()
        self.geom_np = NodePath(self.geom_node)
        self.rigid_np = NodePath(self.rigid_node)
        self.geom_np.reparentTo(self.rigid_np)

    def setBulletShape(self):
        geom = self.toGeom()
        self.mesh.addGeom(geom)
        self.rigid_shape = BulletTriangleMeshShape(self.mesh, dynamic=True)
        self.rigid_node.addShape(self.rigid_shape)

    def setBulletShapeElementWise(self):
        for triangle in self.hyperEdgeLevelDict[self.maxLevel]:
            # FIXME: add a new list called leaves
            p0, p1, p2 = tuple(self.verts2point(triangle))
            self.mesh.addTriangle(p0, p1, p2)

    def getVdata(
        self,
        name=None, geom_type: GeomEnums = Geom.UH_static, vformat=format_,

    ):
        if name is None:
            name = self.name
        vdata = GeomVertexData(name, vformat, geom_type)
        coord = self.getXYZ().cpu().numpy()
        vdataSetNumpy(vdata, coord, field_code='vertex')  # 0 for position
        return vdata

    def toGeom(
        self,
        name=None, geom_type: GeomEnums = Geom.UH_static, vformat=format_,
    ) -> Geom:
        # TODO: sort faces clockwise
        if name is None:
            name = self.name
        vdata = GeomVertexData(name, vformat, geom_type)
        coord = self.getXYZ().cpu().numpy()
        vdataSetNumpy(vdata, coord, field_code='vertex')  # 0 for position
        geom = Geom(vdata)
        prim = GeomTriangles(geom_type)
        for triangle in self.hyperEdgeLevelDict[self.maxLevel]:
            p0, p1, p2 = tuple(triangle.vertIndexes())
            prim.addVertices(p0, p1, p2)
        geom.addPrimitive(prim)
        return geom

    def setGeom(
        self, geom_type: GeomEnums = Geom.UH_static, vformat=format_
    ):
        geom = self.toGeom(
            name=self.name, geom_type=geom_type, vformat=vformat)
        self.geom_node.addGeom(geom)

    def setBulletAndGeom(
        self, geom_type: GeomEnums = Geom.UH_static, vformat=format_
    ):
        geom = self.toGeom(
            name=self.name, geom_type=geom_type, vformat=vformat)
        self.geom_node.addGeom(geom)
        self.mesh.addGeom(geom)
        self.rigid_shape = BulletTriangleMeshShape(self.mesh, dynamic=True)
        self.rigid_node.addShape(self.rigid_shape)

    def verts2point(self, verts: List[SphericalVertInfo]):
        idxs = [vert.idx for vert in verts]
        rho = self.getHeight(idxs)
        theta_phi = torch.Tensor([list(vert.tup) for vert in verts])
        xyz = sphr2cart_pt(theta_phi[:, 0], theta_phi[:, 1]) * rho
        points = [
            Point3(xyz[i, 0], xyz[i, 1], xyz[i, 2])
            for i in range(len(verts))
        ]
        return points
