# -*- coding: utf-8-*-

from panda3d.core import GeomVertexArrayFormat
from typing import Dict, Literal, Tuple
from typing import List, Dict, Tuple
from torch import Tensor, vstack, equal
from panda3d.core import GeomPrimitive
import numpy as np

from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexArrayData,
    GeomVertexArrayDataHandle,
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
    a, b, c, d = tuple(points_idx)
    prim.addVertices(a, b, c)
    prim.addVertices(a, c, d)


def addFace(prim, points_idx):
    if len(points_idx) == 3:
        a, b, c = tuple(points_idx)
        prim.addVertices(a, b, c)
    elif len(points_idx) == 4:
        addQuadrilateral(prim, points_idx)
    else:
        raise NotImplementedError


def add_faces(
    prim: GeomPrimitive,
    faces: List[Tensor],
    vformat=format_uv,
    start_idx=0,
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


def createPosIndicatorNPth(parent: NodePath,
                           nodes: Dict["str", Tuple[float, float, float]],
                           node_name_prefix="") -> Dict["str", NodePath]:
    # FIXME: move this
    # a single node path specifying a position
    ret = {}
    for key in nodes:
        node_path = parent.attachNewNode("{}{}".format(node_name_prefix, key))
        pos = nodes[key]
        node_path.setPos(*pos)
        ret[key] = node_path
    return ret


def getFormatField(
        vformat: GeomVertexArrayFormat) -> Dict[str, Tuple[int, int]]:
    n_col = vformat.getNumColumns()
    field_lengths = [c.getTotalBytes() for c in vformat.columns]
    field_dict = {
        str(vformat.columns[i].getName()):
            (sum(field_lengths[:i]), sum(field_lengths[:i+1]))
        for i in range(n_col)
    }
    return field_dict


def getFormatLength(vformat: GeomVertexArrayFormat) -> int:
    return sum([c.getTotalBytes() for c in vformat.columns])


def vdataSetNumpy(
    vdata: GeomVertexData, arr: np.ndarray,
    field_code: str = 'vertex'
):
    """

    field_code = 0 for position
    codes for other fields depend on the format
    for example for v3c4 color's code is 1
    """
    encode = {
        'vertex': np.float32,
        'color': np.uint8,
        # TODO: uv, norm
    }
    if field_code not in encode:
        raise NotImplementedError
    element_format = encode[field_code]
    element_size = np.dtype(element_format).itemsize
    # TODO: for color, convert float to int
    # FIXME: please have color converted before calling this function
    arr = arr.astype(element_format)
    n_rows = arr.shape[0]
    arr_to_modify: GeomVertexArrayData = vdata.modifyArray(0)
    vformat = arr_to_modify.array_format
    field_dict = getFormatField(vformat)
    field_col_total = getFormatLength(vformat) // element_size
    startbyte, endbyte = field_dict[field_code]
    startcol, endcol = startbyte // element_size, endbyte // element_size
    # TODO
    handle: GeomVertexArrayDataHandle = arr_to_modify.modifyHandle()
    prev_data = handle.getData()
    if len(prev_data) == 0:
        prev_data_np = np.zeros(
            shape=(n_rows, field_col_total),
            dtype=element_format)
    else:
        # TODO: select rows
        prev_data_np = np.frombuffer(prev_data, element_format)
        prev_data_np.resize(n_rows, field_col_total)
    prev_data_np[:, startcol:endcol] = arr
    handle.setData(prev_data_np.tobytes())
