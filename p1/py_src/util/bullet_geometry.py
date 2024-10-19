# -*- coding: utf-8-*-

import torch
from panda3d.core import (
    Geom,Point3,
    GeomVertexReader
)
from panda3d.bullet import (
    BulletShape,
    BulletConvexHullShape
)
def create_convex_hull_shape(geoms):
    # 创建 BulletConvexHullShape
    convex_shape = BulletConvexHullShape()
    # if geoms is a single geom, TODO
    for geom in geoms:
        vdata = geom.getVertexData()
        vertex_reader = GeomVertexReader(vdata, 'vertex')
        while not vertex_reader.isAtEnd():
            vertex = vertex_reader.getData3()
            convex_shape.addPoint(Point3(vertex))
    return convex_shape

def create_convex_hull_shape_tr(geoms, transforms):
    # 创建 BulletConvexHullShape
    convex_shape = BulletConvexHullShape()
    # if geoms is a single geom, TODO
    for i in range(len(geoms)):
    # for geom in geoms:
        geom = geoms[i]
        transform =transforms[i]
        vdata = geom.getVertexData()
        vertex_reader = GeomVertexReader(vdata, 'vertex')
        while not vertex_reader.isAtEnd():
            vertex = vertex_reader.getData3()
            vertex = transform.xformPoint(vertex)
            convex_shape.addPoint(Point3(vertex))
    return convex_shape

def create_chain_shape(points:torch.Tensor) -> BulletShape:
    pass
