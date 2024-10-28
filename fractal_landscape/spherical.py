from typing import Union, Dict, Tuple, List
import torch
import sympy as sp
import networkx
import numpy as np
from util_ import *

class VertInfo:
    pass

class HyperEdge:
    def __init__(self, x:VertInfo, y:VertInfo, z:VertInfo):
        self.x = x
        self.y = y
        self.z = z
        # FIXME
        self._sorted = sorted([x,y,z], key=lambda arg:hash(arg))
        self.resolution = None

    def __hash__(self):
        return hash(self._sorted)

    def edges(self):
        return [
            (self.x,self.y),
            (self.y,self.z),
            (self.z,self.x)
        ]

    def __repr__(self):
        return "【{}, {}, {}】".format(self.x,self.y,self.z)



class SphericalVertInfo(VertInfo):
    def __init__(self, theta:Union[float,sp.Expr], phi:Union[float,sp.Expr]):
        if isinstance(theta, sp.Expr) or isinstance(phi, sp.Expr):
            self.isSymbolic= True
        self.theta = theta
        self.phi = phi
        self.tup = (theta, phi)
        self.idx = None  # index in a list
        self.height_components = {}
        # TODO: register different idx for different list

    def __hash__(self):
        # unique identifier
        return self.tup.__hash__()

    def height_column(self) -> torch.Tensor:
        return torch.Tensor(self.height_components.values())

    def height(self):
        pass

    def angularSphericalDistance(self, theta, phi):
        return angular_spherical_distance(
            phi1 = float(self.phi),
            phi2=float(phi),
            theta1=float(self.theta),
            theta2=float(theta)
    )

    def __iter__(self):
        return iter(self.tup)

    def __len__(self):
        return len(self.tup)

    def __eq__(self, other):
        return self.tup == tuple(other)

    def __ge__(self, other):
        return self.tup >= tuple(other)

    def __gt__(self, other):
        return self.tup > tuple(other)

    def float(self):
        return (float(self.theta),float(self.phi))

    def hyperedge_code(self, graph):
        # represent this vert using a list of hyperedges
        pass

    def getMidPoint(self, other):
        pass

    def __repr__(self):
        return "SphericalVertInfo({},{})".format(self.theta, self.phi)


from icosahedron import icosahedron_coords, icosahedron_faces
icosahedron_verts = [
    SphericalVertInfo(theta, phi)
    for (theta, phi) in icosahedron_coords
]
icosahedron_hyper_edges = [
    HyperEdge(
        icosahedron_verts[i],
        icosahedron_verts[j],
        icosahedron_verts[k]
    ) for (i,j,k) in icosahedron_faces
]
# split phi and theta

# vert coordinate from Icosahedron

# create verts from list

class SphereMesh:
    def __init__(self):
        self.verts = []
        # verts:
        # a list for all vert id
        #  - node unique identifier
        #  - node index in list
        # map id to coordinate theta and phi
        #   use node property
        # map id to height
        # edges: all connected verts
        self.midpoints:Dict[Tuple[VertInfo,VertInfo], VertInfo] = {}
        # FIXME: use hashed set
        # a dictionary for edges and their midpoints
        # hyperedges: all triangles
        # containship graph
        # hyperedges <-> verts inside (bipartite)
        # splitship graph
        # hyperedge - child hyperedges
        # lists for batch split
        # a list for hyperedges each batch of split

    def uniform_split(self, iterations:int):
        iterations = int(iterations)


    # method: retrieve a tensor for all verts theta and phi
    # mothod: retrieve a tensor for all verts heightmap (optional)

    # create a planet
    # split to N
    # then random sample (phi, theta, size, other param) x m as craters
    # for each crate
    # calculate distance from each hyperedge
    # pooled_val(f, v1,v2,v3)
    #  ->  can use different kernel for this
    #  ->  use monotonicity if function

    # if close to ridge, the split

    # get splitted hyperedges

    # calculate heightmap for each vert
    # given each crater



if __name__ == "__main__":
    print(icosahedron_verts)
