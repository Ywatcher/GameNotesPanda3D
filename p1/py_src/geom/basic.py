import torch
from numpy import cos, pi, sin
import numpy as np
from py_src.util.indexing import loop_bound_idx, tup2cnt


from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GeomEnums
)
# Declare the format of the vertex
# (what and how data will be stored in the vertex buffer)
# https://docs.panda3d.org/1.10/python/programming/internal-structures/procedural-generation/custom-vertex-format
# https://docs.panda3d.org/1.10/python/programming/internal-structures/procedural-generation/predefined-vertex-formats
format_ = GeomVertexFormat.getV3c4()
format_ = GeomVertexFormat.registerFormat(format_)


def uv_curve_surface(
    name:str, 
    coord_mat:torch.Tensor, is_u_loop:bool, is_v_loop:bool,
    geom_type: GeomEnums = Geom.UH_static, vformat=format_
) -> Geom:
    # coord_mat: [u_size, v_size, format_size]
    u_size = coord_mat.shape[0]
    v_size = coord_mat.shape[1]
    vertex_size = (u_size, v_size)
    vdata = GeomVertexData(name, vformat, geom_type)
    vertex_writer = GeomVertexWriter(vdata, "vertex")
    # vertex_size = (lon_res, lat_res)
    for row in range(u_size):
        for col in range(v_size):
            coord = coord_mat[row, col]
            vertex_writer.addData3f(
                coord[0], coord[1], coord[2]
            )
            # TODO: add colour
    # add triangles
    prim = GeomTriangles(geom_type)
    for row in range(u_size - (not is_u_loop)):
        for col in range(v_size - (not is_v_loop)):
            prim.addVertices(
                tup2cnt(vertex_size, row, col),
                tup2cnt(vertex_size, row+1, col),
                tup2cnt(vertex_size, row, col+1)               
            )
            prim.addVertices(
                tup2cnt(vertex_size, row+1, col),
                tup2cnt(vertex_size, row, col+1),
                tup2cnt(vertex_size, row+1, col+1)
            )
    geom = Geom(vdata)
    geom.addPrimitive(prim)  
    return geom

# def uv_curve_table(
#     name:str, 
#     coord_mat:torch.Tensor, top:bool, bot:bool,
#     geom_type: GeomEnums = Geom.UH_static, vformat=format_
# ) -> Geom:
#     side_geom = 

def create_sphere_node(
    name:str,
    lat_res:int,
    lon_res:int,
    # scale:float=1,
    geom_type: GeomEnums = Geom.UH_static
) -> GeomNode:
    node = GeomNode("SphNd."+name)
    geom = create_sphere(
        name, lat_res, lon_res,
        # scale, 
        geom_type
    )
    node.addGeom(geom)
    return node

def create_sphere(
    name:str,
    lat_res:int,
    lon_res:int,
    scale:float=1,
    geom_type: GeomEnums = Geom.UH_static
) -> Geom:
    assert isinstance(lat_res, int) \
        and lat_res > 0, \
        "lat_res should be postive int, got {}".format(lat_res)
    name_sphere = "Spr.{}".format(name)
    vertex_size = (lon_res, lat_res)
    # color = GeomVertexWriter(vdata, "color")
    # vertex: n_lat * n_lon * 3
    axis_coord_theta = torch.arange(0,1,step=1/lon_res) * 2 * np.pi
    axis_coord_phi = torch.arange(0,1,step=1/lat_res) * 2 * np.pi
    vertex_coord_theta = torch.broadcast_to(axis_coord_theta.view(-1, 1), vertex_size)
    vertex_coord_phi = torch.broadcast_to(axis_coord_phi.view(1, -1), vertex_size)
    vertex_coord_r = torch.cos(vertex_coord_phi)
    vertex_coord_z = torch.sin(vertex_coord_phi)
    vertex_coord_x = torch.cos(vertex_coord_theta) * vertex_coord_r
    vertex_coord_y = torch.sin(vertex_coord_theta) * vertex_coord_r
    vertex_coord_xyz = torch.concat([
        vertex_coord_x.unsqueeze(-1),
        vertex_coord_y.unsqueeze(-1),
        vertex_coord_z.unsqueeze(-1)
    ], dim=-1)

    geom = uv_curve_surface(
        name=name_sphere,
        coord_mat=vertex_coord_xyz,
        is_u_loop=False, # for lat: not loop
        is_v_loop=True,
        geom_type = geom_type
    )
    
    return geom

def create_cube_node(
    name:str,
    geom_type: GeomEnums = Geom.UH_static, vformat=format_
) -> GeomNode:
    node = GeomNode("CbNd."+name)
    geom = create_cube(name, geom_type, vformat)
    node.addGeom(geom)
    return node

def create_cube(
    name:str,  #TODO: name_postfix
    geom_type: GeomEnums = Geom.UH_static, vformat=format_
) -> Geom:
    name_cube = "Cb.{}".format(name)
    # Instantiate a vertex buffer
    # https://docs.panda3d.org/1.10/python/programming/internal-structures/procedural-generation/creating-vertex-data
    vdata = GeomVertexData(name, vformat, geom_type)
    vertex = GeomVertexWriter(vdata, "vertex")
    color = GeomVertexWriter(vdata, "color")

    # Add vertices and colors
    vertex.addData3f(-1, -1, -1)
    color.addData4f(0, 0, 0, 1)

    vertex.addData3f(-1, -1, 1)
    color.addData4f(0, 0, 1, 1)

    vertex.addData3f(-1, 1, -1)
    color.addData4f(0, 1, 0, 1)

    vertex.addData3f(-1, 1, 1)
    color.addData4f(0, 1, 1, 1)

    vertex.addData3f(1, -1, -1)
    color.addData4f(1, 0, 0, 1)

    vertex.addData3f(1, -1, 1)
    color.addData4f(1, 0, 1, 1)

    vertex.addData3f(1, 1, -1)
    color.addData4f(1, 1, 0, 1)

    vertex.addData3f(1, 1, 1)
    color.addData4f(1, 1, 1, 1)

    # Create the triangles (2 per face)
    # https://docs.panda3d.org/1.10/python/programming/internal-structures/procedural-generation/creating-primitives
    # prim = GeomTriangles(Geom.UHStatic)
    prim = GeomTriangles(geom_type)
    prim.addVertices(0, 1, 2)
    prim.addVertices(2, 1, 3)
    prim.addVertices(2, 3, 6)
    prim.addVertices(6, 3, 7)
    prim.addVertices(6, 7, 4)
    prim.addVertices(4, 7, 5)
    prim.addVertices(4, 5, 0)
    prim.addVertices(0, 5, 1)
    prim.addVertices(1, 5, 3)
    prim.addVertices(3, 5, 7)
    prim.addVertices(6, 4, 2)
    prim.addVertices(2, 4, 0)

    geom = Geom(vdata)
    geom.addPrimitive(prim)
    # node = GeomNode("node")
    # node.addGeom(geom)

    return geom

