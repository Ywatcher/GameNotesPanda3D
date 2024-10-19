# -*- coding: utf-8-*-

from typing import List, Dict, Tuple
from torch import Tensor, vstack, equal
from panda3d.core import GeomPrimitive

from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GeomEnums,
    NodePath,
    TransformState,
    Mat4
)
format_ = GeomVertexFormat.getV3c4()
format_uv = GeomVertexFormat.getV3t2()
format_ = GeomVertexFormat.registerFormat(format_)

# TODO: merge indexing and geometry

def batch_transform(
    faces: List[Tensor], transformations: List[Tensor]
) -> List[Tensor]:
    return [
        face @ transformation
        for face in faces
        for transformation in transformations
    ]

def makeLookAt(vec):
    # m = Mat4()
    # # TODO: convert to Vec3
    # m.lookAt(vec)
    # tr = TransformState.makeMat(m)
    # return tr
    temp_np = NodePath('temp_np')
    temp_np.set_pos(0, 0, 0)  # The starting position of the rigid body

    # Make it look at the target
    temp_np.lookAt(vec)

    # Extract the transformation
    # from the temporary NodePath
    tr = temp_np.get_transform()
    return tr

def addQuadrilateral(prim, points_idx):
    a,b,c,d = tuple(points_idx)
    prim.addVertices(a,b,c)
    prim.addVertices(a,c,d)

def addFace(prim, points_idx):
    if len(points_idx) == 3:
        a,b,c = tuple(points_idx)
        prim.addVertices(a,b,c)
    elif len(points_idx) == 4:
        addQuadrilateral(prim, points_idx)
    else:
        raise NotImplementedError

def add_faces(
    prim: GeomPrimitive,
    faces:List[Tensor],
    vformat=format_uv,
    start_idx = 0,
    name=""
):
    # indexing all vertices
    uh = prim.getUsageHint()
    verts = list(
        set(
            tuple(row.numpy())
            # row
            for row in vstack(faces)
        )
    )
    verts = [
        Tensor(v) for v in verts
    ]

    # create vertex writer
    vdata = GeomVertexData(name, vformat, uh)
    vertex_writer = GeomVertexWriter(vdata, "vertex")
    # add vertex and index them
    for vert in verts:
        vertex_writer.addData3f(
            vert[0], vert[1], vert[2]
        )
    def face_vertex_coord_2_index(face_, all_verts_, start_idx):
        face_with_index = []
        for row in face_:
            for (i, vert) in enumerate(all_verts_):
                if equal(row, vert):
                    face_with_index.append(i+start_idx)
        return face_with_index
    for face in faces:
        face_with_index = face_vertex_coord_2_index(face, verts, start_idx)
        addFace(prim, face_with_index)
    return vdata, start_idx + len(verts)


def createPosIndicatorNPth(
    parent:NodePath, nodes:Dict["str", Tuple[float,float,float]], node_name_prefix=""
) -> Dict["str", NodePath]:
    # FIXME: move this
    # a single node path specifying a position
    ret = {}
    for key in nodes:
        node_path = parent.attachNewNode("{}{}".format(node_name_prefix, key))
        pos = nodes[key]
        node_path.setPos(*pos)
        ret[key] = node_path
    return ret
