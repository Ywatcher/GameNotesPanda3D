import torch
from numpy import cos, pi, sin
import numpy as np
from util.indexing import loop_bound_idx, tup2cnt


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
format_uv = GeomVertexFormat.getV3t2()
format_ = GeomVertexFormat.registerFormat(format_)


def uv_curve_surface(
    name:str, 
    coord_mat:torch.Tensor, is_u_loop:bool, is_v_loop:bool,
    uv_mat:torch.Tensor=None, 
    geom_type: GeomEnums = Geom.UH_static, vformat=format_uv
) -> Geom:
    # coord_mat: [u_size, v_size, format_size]
    u_size = coord_mat.shape[0]
    v_size = coord_mat.shape[1]
    vertex_size = (u_size+is_u_loop, v_size+is_v_loop)
    has_uv = (vformat == format_uv) # FIXME
    
    vdata = GeomVertexData(name, vformat, geom_type)
    vertex_writer = GeomVertexWriter(vdata, "vertex")
    if has_uv:
        uv_writer = GeomVertexWriter(vdata, 'texcoord')
        if uv_mat is None:
            u_step = 1 / (u_size-1+is_u_loop)
            v_step = 1 / (v_size-1+is_v_loop)
            u,v = torch.meshgrid(
                
                torch.arange(0,1+u_step,step=u_step), #FIXME:[0,1+step)
                torch.arange(0,1+v_step,step=v_step)
            )
            uv_mat = torch.concat(
                [u.unsqueeze(-1), v.unsqueeze(-1)], dim=-1
            )
    # vertex_size = (lon_res, lat_res)
    for row in range(u_size + is_u_loop):
        for col in range(v_size + is_v_loop):
            coord = coord_mat[row % u_size, col % v_size]
            uv = uv_mat[row,col]
            vertex_writer.addData3f(
                coord[0], coord[1], coord[2]
            )
            if has_uv:
                uv_writer.addData2f(
                    uv[0], uv[1]
                )
    # add triangles
    prim = GeomTriangles(geom_type)
    for row in range(u_size - (not is_u_loop)):
        for col in range(v_size - (not is_v_loop)):
            # prim.addVertices(
            #     tup2cnt(vertex_size, row, col),
            #     tup2cnt(vertex_size, row+1, col),
            #     tup2cnt(vertex_size, row, col+1)               
            # )
            prim.addVertices(
                tup2cnt(vertex_size, row+1, col),
                tup2cnt(vertex_size, row, col+1),
                tup2cnt(vertex_size, row+1, col+1)
            )
            prim.addVertices(
                tup2cnt(vertex_size, row+1, col),
                tup2cnt(vertex_size, row, col),
                tup2cnt(vertex_size, row, col+1)               
            )
            # prim.addVertices(
            #     tup2cnt(vertex_size, row, col+1),
            #     tup2cnt(vertex_size, row+1, col),
            #     tup2cnt(vertex_size, row+1, col+1)
            # )
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
    # vertex_size = (lon_res, lat_res)
    # color = GeomVertexWriter(vdata, "color")
    # vertex: n_lat * n_lon * 3
    axis_coord_theta = torch.arange(0,1,step=1/lon_res) * 2 * np.pi
    axis_coord_phi = torch.arange(0,1,step=1/lat_res) * 2 * np.pi
    vertex_coord_theta, vertex_coord_phi = torch.meshgrid(
        axis_coord_theta,axis_coord_phi,
        indexing='ij'
    )
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
        is_u_loop=True,
        is_v_loop=False, 
        geom_type = geom_type
    )
    
    return geom

def create_cube_node():
    pass

def create_cube():
    pass

def create_colored_cube_node(
    name:str,
    geom_type: GeomEnums = Geom.UH_static, vformat=format_
) -> GeomNode:
    node = GeomNode("CbNd."+name)
    geom = create_colored_cube(name, geom_type, vformat)
    node.addGeom(geom)
    return node

def create_colored_cube(
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

# TODO: intersections

def create_cylinder_node(
    name:str,
    lat_res:int,
    lon_res:int,
    # scale:float=1,
    geom_type: GeomEnums = Geom.UH_static
) -> GeomNode:
    node = GeomNode("CldrNd."+name)
    geom = create_cylinder(
        name, lat_res, lon_res,
        # scale, 
        geom_type
    )
    node.addGeom(geom)
    return node

# TODO: fix 

def create_cylinder(
    name:str,
    lat_res:int,
    lon_res:int,
    scale:float=1,
    geom_type: GeomEnums = Geom.UH_static
) -> Geom:
    assert isinstance(lat_res, int) \
        and lat_res > 0, \
        "lat_res should be postive int, got {}".format(lat_res)
    name_cylinder = "Cldr.{}".format(name)
    # vertex_size = (lon_res, lat_res)
    # color = GeomVertexWriter(vdata, "color")
    # vertex: n_lat * n_lon * 3
    axis_coord_theta = torch.arange(0,1,step=1/lon_res) * 2 * np.pi
    # axis_coord_phi = torch.arange(0,1,step=1/lat_res) * 2 * np.pi
    axis_coord_z = torch.arange(0,1,step=1/lat_res)
    vertex_coord_theta, vertex_coord_z = torch.meshgrid(
        axis_coord_theta,axis_coord_z,
        indexing='ij'
    )
    # vertex_coord_r = torch.cos(vertex_coord_phi)
    vertex_coord_r = 1
    # vertex_coord_z = torch.sin(vertex_coord_phi)
    # vertex_coord_z = 
    vertex_coord_x = torch.cos(vertex_coord_theta) * vertex_coord_r
    vertex_coord_y = torch.sin(vertex_coord_theta) * vertex_coord_r
    vertex_coord_xyz = torch.concat([
        vertex_coord_x.unsqueeze(-1),
        vertex_coord_y.unsqueeze(-1),
        vertex_coord_z.unsqueeze(-1)
    ], dim=-1)

    geom = uv_curve_surface(
        name=name_cylinder,
        coord_mat=vertex_coord_xyz,
        is_u_loop=True,
        is_v_loop=False, 
        geom_type = geom_type
    )
    
    return geom