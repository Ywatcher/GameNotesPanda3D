# -*- coding: utf-8-*-

from typing import Callable, List
import torch
from numpy import cos, pi, sin
import numpy as np

from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GeomEnums,
    InternalName
)
from util.indexing import loop_bound_idx, tup2cnt
# Declare the format of the vertex
# (what and how data will be stored in the vertex buffer)
# https://docs.panda3d.org/1.10/python/programming/internal-structures/procedural-generation/custom-vertex-format
# https://docs.panda3d.org/1.10/python/programming/internal-structures/procedural-generation/predefined-vertex-formats
from util.geometry import *
from util.maths import compute_uv_normals
# TODO: close prim

def geom_frm_faces(
    name:str,
    faces: List[torch.Tensor],
    geom_type: GeomEnums=Geom.UH_static,
    vformat=format_uv
) -> Geom:
    prim = GeomTriangles(geom_type)
    vdata, vert_idx = add_faces(
        prim=prim, faces=faces, vformat=vformat,
        start_idx=0, name=name
    )
    geom = Geom(vdata)
    geom.addPrimitive(prim)
    return geom

# FIXME: import



def uv_curve_surface_lambda(
    name:str,
    u:torch.Tensor,
    v:torch.Tensor,
    is_u_loop:bool, is_v_loop:bool,
    x_uv:Callable,
    y_uv:Callable,
    z_uv:Callable,
    geom_type: GeomEnums = Geom.UH_static, vformat=format_uv,
    interior:bool=False
) -> Geom:
    u_broadcast, v_broadcast = torch.meshgrid(u,v,indexing='ij')
    vertex_coord_x = x_uv(u_broadcast,v_broadcast)
    vertex_coord_y = y_uv(u_broadcast,v_broadcast)
    vertex_coord_z = z_uv(u_broadcast,v_broadcast)
    vertex_coord_xyz = torch.concat([
        vertex_coord_x.unsqueeze(-1),
        vertex_coord_y.unsqueeze(-1),
        vertex_coord_z.unsqueeze(-1)
    ], dim=-1)
    # vertex_norm_xyz = ...
    geom = uv_curve_surface(
        name=name,
        coord_mat=vertex_coord_xyz,
        # normal_mat=vertex_norm_xyz,
        is_u_loop=is_u_loop,
        is_v_loop=is_v_loop,
        geom_type = geom_type,
        vformat=vformat,
        interior=interior
    )
    return geom

# smooth curve surface 
def uv_curve_surface(
    name:str,
    coord_mat:torch.Tensor, is_u_loop:bool, is_v_loop:bool,
    uv_mat:torch.Tensor=None,  #uv mapping
    normal_mat:torch.Tensor=None,
    geom_type: GeomEnums = Geom.UH_static, vformat=format_uv,
    interior:bool=False,
) -> Geom:
    """
    smooth curve surface generator 
    if normal added, it will be vertex normal vector, 
    i.e. face normal vector, when used in fragment shader,
    will be interpolated using shared vertex vectors
    so it will look smooth.
    """
    # FIXME: add normal if there is a normal field in format 
    # FIXME: if there is normal argument, but not normal field, then give warning
    # coord_mat: [u_size, v_size, format_size]
    if interior:
        uv_mat = uv_mat[:,:,::-1]
    u_size = coord_mat.shape[0]
    v_size = coord_mat.shape[1]
    vertex_size = (u_size+is_u_loop, v_size+is_v_loop)
    
    has_uv = format_has_column(vformat, InternalName.getTexcoord())
    has_normal = format_has_column(vformat, InternalName.getNormal()) 

    vdata = GeomVertexData(name, vformat, geom_type)
    vertex_writer = GeomVertexWriter(vdata, "vertex")
    if has_normal:
        normal_writer = GeomVertexWriter(vdata, "normal") 
        if normal_mat is None :
            normal_mat = compute_uv_normals(coord_mat, is_u_loop, is_v_loop)
        # if interior:
            # normal_mat = normal_mat * -1
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
            if has_normal:
                normal = normal_mat[row % u_size, col % v_size]
                normal_writer.addData3f(
                    normal[0], normal[1], normal[2]
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
    geom_type: GeomEnums = Geom.UH_static,
    vformat=format_uv,
    interior:bool=False
) -> GeomNode:
    node = GeomNode("SphNd."+name)
    geom = create_sphere(
        name, lat_res, lon_res,
        # scale,
        geom_type=geom_type,
        vformat=vformat,
        interior=interior
    )
    node.addGeom(geom)
    return node

def create_sphere(
    name:str,
    lat_res:int,
    lon_res:int,
    scale:float=1,
    geom_type: GeomEnums = Geom.UH_static,
    vformat=format_uv,
    interior:bool=False
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
    vertex_norm = vertex_coord_xyz.clone()

    geom = uv_curve_surface(
        name=name_sphere,
        coord_mat=vertex_coord_xyz,
        normal_mat=vertex_norm,
        is_u_loop=True,
        is_v_loop=False,
        geom_type = geom_type,
        vformat=vformat,
        interior=interior
    )

    return geom

def create_cube_node():
    pass

def create_cube():
    pass

def create_colored_cube_node(
    name:str,
    geom_type: GeomEnums = Geom.UH_static, 
    vformat=format_v3c4,
    smooth: bool = False
) -> GeomNode:
    node = GeomNode("CbNd."+name)
    geom = create_colored_cube(name, geom_type, vformat, smooth)
    node.addGeom(geom)
    return node

def create_colored_cube(
    name:str,  #TODO: name_postfix
    geom_type: GeomEnums = Geom.UH_static, 
    vformat:GeomVertexFormat = format_v3c4, 
    smooth: bool = False
) -> Geom:
    name_cube = "Cb.{}".format(name)
    # Instantiate a vertex buffer
    # https://docs.panda3d.org/1.10/python/programming/internal-structures/procedural-generation/creating-vertex-data
    vdata = GeomVertexData(name, vformat, geom_type)
    vertex = GeomVertexWriter(vdata, "vertex")
    if formatHasColumn(vformat, "color"):
        color = GeomVertexWriter(vdata, "color")
    else: 
        color = EmptyVertexWriter(vdata, "color")
    if formatHasColumn(vformat, "normal"):
        normal = GeomVertexWriter(vdata, "normal")
    else:
        normal = EmptyVertexWriter(vdata, "normal")
        smooth = True

    if smooth:
        # Add vertices and colors
        vertex.addData3f(-1, -1, -1)
        normal.addData3f(-1, -1, -1)
        color.addData4f(0, 0, 0, 1)

        vertex.addData3f(-1, -1, 1)
        normal.addData3f(-1, -1, 1)
        color.addData4f(0, 0, 1, 1)

        vertex.addData3f(-1, 1, -1)
        normal.addData3f(-1, 1, -1)
        color.addData4f(0, 1, 0, 1)

        vertex.addData3f(-1, 1, 1)
        normal.addData3f(-1, 1, 1)
        color.addData4f(0, 1, 1, 1)

        vertex.addData3f(1, -1, -1)
        normal.addData3f(1, -1, -1)
        color.addData4f(1, 0, 0, 1)

        vertex.addData3f(1, -1, 1)
        normal.addData3f(1, -1, 1)
        color.addData4f(1, 0, 1, 1)

        vertex.addData3f(1, 1, -1)
        normal.addData3f(1, 1, -1)
        color.addData4f(1, 1, 0, 1)

        vertex.addData3f(1, 1, 1)
        normal.addData3f(1, 1, 1)
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
    else:
        # TODO : validate
        # flat cube: 6 faces * 4 vertices = 24 vertices
        face_defs = [
            # (face normal, list of 4 vertices)
            ((0,0,1),  [(-1,-1,1), (1,-1,1), (-1,1,1), (1,1,1)]),   # front
            ((0,0,-1), [(-1,-1,-1), (-1,1,-1), (1,-1,-1), (1,1,-1)]), # back
            ((1,0,0),  [(1,-1,-1), (1,1,-1), (1,-1,1), (1,1,1)]),    # right
            ((-1,0,0), [(-1,-1,-1), (-1,-1,1), (-1,1,-1), (-1,1,1)]), # left
            ((0,1,0),  [(-1,1,-1), (-1,1,1), (1,1,-1), (1,1,1)]),     # top
            ((0,-1,0), [(-1,-1,-1), (1,-1,-1), (-1,-1,1), (1,-1,1)]), # bottom
        ]
        prim = GeomTriangles(geom_type)
        idx = 0
        for normal_vec, verts in face_defs:
            for v in verts:
                vertex.addData3f(*v)
                color.addData4f( (v[0]+1)/2, (v[1]+1)/2, (v[2]+1)/2, 1 )  # color indicated by location 
                normal.addData3f(*normal_vec)
            # two triangles per face
            prim.addVertices(idx, idx+1, idx+2)
            prim.addVertices(idx+2, idx+1, idx+3)
            idx += 4

    geom = Geom(vdata)
    geom.addPrimitive(prim)
    # node = GeomNode("node")
    # node.addGeom(geom)

    return geom

# TODO: intersections
import operator
def create_cylinder_node(
    name:str,
    # lat_res:int,
    lon_res:int,
    # scale:float=1,
    radius=1,
    height=1,
    height_bot=0,
    geom_type: GeomEnums = Geom.UH_static,
    interior:bool=False,
    with_top=True,
    with_bot=True,
    smooth_top=False,
    smooth_bot=False
) -> GeomNode:
    node = GeomNode("CldrNd."+name)
    geoms = []
    if with_top and not smooth_top:
        top = create_pan(
            name,
            lon_res,
            radius,
            height,
            geom_type,
            face_above = True,
            interior = interior
        )
        geoms.append(top)
    main_part = create_cylinder(
        name, lon_res,
        # scale,
        radius, height, height_bot,
        geom_type,
        interior,
        with_top and smooth_top,
        with_bot and smooth_bot
    )
    geoms.append(main_part)
    if with_bot and not smooth_bot:
        bot = create_pan(
            name,
            lon_res,
            radius,
            height_bot,
            geom_type,
            face_above = False,
            interior = interior
        )
        geoms.append(bot)
    for geom in geoms:
        node.addGeom(geom)
    return node

# TODO: fix

def create_cylinder(
    name:str,
    lon_res:int,
    radius=1,
    height=1,
    height_bot=0,
    geom_type: GeomEnums = Geom.UH_static,
    interior:bool=False,
    with_top=True,
    with_bot=True,
) -> Geom:
    name_cylinder = "Cldr.{}".format(name)
    axis_coord_theta = torch.arange(0,1,step=1/lon_res) * 2 * np.pi
    axis_coord_y = torch.Tensor([height,height_bot])
    vertex_coord_theta, vertex_coord_y = torch.meshgrid(
        axis_coord_theta,axis_coord_y,
        indexing='ij'
    )
    vertex_coord_r = radius
    vertex_coord_x = torch.cos(vertex_coord_theta) * vertex_coord_r
    vertex_coord_z = torch.sin(vertex_coord_theta) * vertex_coord_r

    # shape: [n_vertex, 3]
    vertex_coord_xyz = torch.concat([
        vertex_coord_x.unsqueeze(-1),
        vertex_coord_y.unsqueeze(-1),
        vertex_coord_z.unsqueeze(-1)
    ], dim=-1)
    vertex_norm_xyz = torch.concat([
        vertex_coord_x.unsqueeze(-1),
        vertex_coord_y.unsqueeze(-1) * 0,
        vertex_coord_z.unsqueeze(-1)
    ], dim=-1)
    if with_top:
        top = torch.ones([lon_res,1,3]) * torch.Tensor([0,height,0])
        top_norm = torch.ones([lon_res,1,3]) * torch.Tensor([0,1,0])
        vertex_coord_xyz = torch.concat([
            top,
            vertex_coord_xyz,
        ], axis=1)
        vertex_norm_xyz = torch.concat([
            top_norm, vertex_norm_xyz
        ], axis=1)
    if with_bot:
        bot = torch.ones([lon_res,1,3]) * torch.Tensor([0,height_bot,0])
        bot_norm = torch.ones([lon_res,1,3]) * torch.Tensor([0,-1,0])
        vertex_coord_xyz = torch.concat([
            vertex_coord_xyz,
            bot,
        ], axis=1)
        vertex_norm_xyz = torch.concat([
            vertex_norm_xyz, bot_norm
        ], axis=1)

    geom = uv_curve_surface(
        name=name_cylinder,
        coord_mat=vertex_coord_xyz,
        normal_mat=vertex_norm_xyz,
        is_u_loop=True,
        is_v_loop=False,
        geom_type = geom_type,
        interior=interior
    )

    return geom

def create_pan(
        name: str, 
        lon_res:int,
        radius=1,
        height=0,
        geom_type: GeomEnums = Geom.UH_static,
        face_above=True,
        interior=False
        ):
    name_pan = "Pan.{}".format(name)
    axis_coord_theta = torch.arange(0,1,step=1/lon_res) * 2 * np.pi
    axis_coord_y = torch.Tensor([height])
    vertex_coord_theta, vertex_coord_y = torch.meshgrid(
        axis_coord_theta,axis_coord_y,
        indexing='ij'
    )
    vertex_coord_r = radius
    vertex_coord_x = torch.cos(vertex_coord_theta) * vertex_coord_r
    vertex_coord_z = torch.sin(vertex_coord_theta) * vertex_coord_r
    vertex_coord_xyz = torch.concat([
        vertex_coord_x.unsqueeze(-1),
        vertex_coord_y.unsqueeze(-1),
        vertex_coord_z.unsqueeze(-1)
    ], dim=-1)
    center =  torch.ones([lon_res,1,3]) * torch.Tensor([0,height,0])
    if face_above:
        vertex_coord_xyz = torch.concat([
            center,
            vertex_coord_xyz,
        ], axis=1)
        vertex_norm_xyz = torch.ones_like(vertex_coord_xyz)
    else:
        vertex_coord_xyz = torch.concat([
            vertex_coord_xyz,
            center,
        ], axis=1)
        vertex_norm_xyz = -1 * torch.ones_like(vertex_coord_xyz)
    geom = uv_curve_surface(
        name=name_pan,
        coord_mat=vertex_coord_xyz,
        normal_mat=vertex_norm_xyz,
        is_u_loop=True,
        is_v_loop=False,
        geom_type = geom_type,
        interior=interior
    )
    return geom










def getCylinderShape(radius, height, lon_res):
    axis_coord_theta = torch.arange(0,1,step=1/lon_res) * 2 * np.pi
    # axis_coord_phi = torch.arange(0,1,step=1/lat_res) * 2 * np.pi
    # fixme: set lat res to 1
    # axis_coord_z = torch.arange(0,1,step=1/lat_res)
    convex_shape = BulletConvexHullShape()
    axis_coord_y = torch.Tensor([height,0])
    vertex_coord_theta, vertex_coord_y = torch.meshgrid(
        axis_coord_theta,axis_coord_y,
        indexing='ij'
    )
    # vertex_coord_r = torch.cos(vertex_coord_phi)
    vertex_coord_r = radius
    # vertex_coord_z = torch.sin(vertex_coord_phi)
    # vertex_coord_z =
    vertex_coord_x = torch.cos(vertex_coord_theta) * vertex_coord_r
    vertex_coord_z = torch.sin(vertex_coord_theta) * vertex_coord_r

    vertex_coord_xyz = torch.concat([
        vertex_coord_x.unsqueeze(-1),
        vertex_coord_y.unsqueeze(-1),
        vertex_coord_z.unsqueeze(-1)
    ], dim=-1)
    for col in range(2):
        for row in range(lon_res):
            vertex = tuple(vertex_coord_xyz[row,col].numpy())

            convex_shape.addPoint(Point3(vertex))
    return convex_shape
