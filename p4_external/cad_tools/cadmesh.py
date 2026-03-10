
import filepath_p2

from panda3d.core import *
from build123d import *
from panda3d.core import NodePath
from util.geometry import *
import torch

try:
    import build123d
except ImportError:
    import warnings
    warnings.warn("build123d is not installed. build123d_to_panda functions will fail.")


def build123d_to_panda_geom(
    part:"build123d.Part", tol=0.1, format_=None,
    geom_type: GeomEnums = Geom.UH_static
):
    vertices, triangles = part.tessellate(tol)
    if format_ is None:
        format_ = GeomVertexFormat.getV3()
    has_normal = format_has_column(format_, InternalName.getNormal())

    # ---- convert to tensor ----
    vert_tensor = torch.tensor(
        [[v.X, v.Y, v.Z] for v in vertices],
        dtype=torch.float32
    )

    tri_tensor = torch.tensor(
        triangles,
        dtype=torch.long
    )

    vdata = GeomVertexData("mesh", format_, Geom.UHStatic)
    vertex_writer = GeomVertexWriter(vdata, "vertex")

    if has_normal:
        normals = compute_vertex_normals_torch(vert_tensor, tri_tensor)
        normal_writer = GeomVertexWriter(vdata, "normal")
    for i in range(len(vertices)):

        v = vert_tensor[i]
        vertex_writer.addData3f(
            float(v[0]), float(v[1]), float(v[2])
        )
        if has_normal:
            n = normals[i]
            normal_writer.addData3f(
                float(n[0]), float(n[1]), float(n[2])
            )
    prim = GeomTriangles(Geom.UHStatic)
    for a, b, c in triangles:
        prim.addVertices(a, b, c)
    geom = Geom(vdata)
    geom.addPrimitive(prim)
    return geom 

def build123d_to_panda_node(
    part:"build123d.Part",name:str, 
    tol=0.1, format_=None,
    geom_type: GeomEnums = Geom.UH_static
):
    geom = build123d_to_panda_geom(part, tol, format_, geom_type)
    node = GeomNode(name)
    node.addGeom(geom)
    return node

