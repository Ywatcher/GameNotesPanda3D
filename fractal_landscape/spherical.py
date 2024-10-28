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

    def __iter__(self):
        return iter(self._sorted)

    @property
    def edges(self) -> List[Tuple[VertInfo, VertInfo]]:
        return [
            (self.x,self.y),
            (self.y,self.z),
            (self.z,self.x)
        ]

    def __repr__(self):
        return "【{}, {}, {}】".format(self.x,self.y,self.z)



class SphericalVertInfo(VertInfo):
    def __init__(
        self,
        theta:Union[float,sp.Expr], phi:Union[float,sp.Expr],
        parent_mesh:Union[None, "SphereMesh"] = None
    ):
        if isinstance(theta, sp.Expr) or isinstance(phi, sp.Expr):
            self.isSymbolic = True
        else:
            self.isSymbolic = False
        self.theta = theta
        self.phi = phi
        self.tup = (theta, phi)
        self.idx = None  # index in a list
        self.parentMesh = parent_mesh
        # TODO: register different idx for different list

    def __hash__(self):
        # unique identifier
        return self.tup.__hash__()

    # def height_column(self) -> torch.Tensor:
        # return torch.Tensor(self.height_components.values())

    # def height(self):
        # # FIXME
        # if self.parent_mesh is not None:
            # return self.parent_mesh.getHeight(self.idx)
        # else:
            # return 0

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

    def hyperEdgeCode(self, graph):
        # represent this vert using a list of hyperEdges
        pass

    def getMidPoint(self, other) -> VertInfo:
        if self.isSymbolic or other.isSymbolic:
            theta_new, phi_new = spherical_midpoint_sp(
                theta1=self.theta, theta2=other.theta,
                phi1=self.phi, phi2=other.phi
            )
            return SphericalVertInfo(
                theta=theta_new, phi=phi_new, parent_mesh=self.parentMesh)
        else:
            return NotImplemented

    def __repr__(self):
        return "SphericalVertInfo({},{})".format(self.theta, self.phi)


from icosahedron import icosahedron_coords, icosahedron_faces
def getIcosahedronVerts(symbolic) -> List[SphericalVertInfo]:
    if symbolic:
        icosahedron_verts = [
            SphericalVertInfo(theta, phi)
            for (theta, phi) in icosahedron_coords
        ]
    else:
        icosahedron_verts = [
            SphericalVertInfo(
                float(theta.subs(alpha, alpha_val).subs(gamma, gamma_val)),
                float(phi.subs(alpha, alpha_val).subs(gamma, gamma_val))
            )
            for (theta, phi) in icosahedron_coords
        ]
    return icosahedron_verts

def getIcosahedronFaces(verts:None) -> List[HyperEdge]:
    if verts is None:
        verts = getIcosahedronVerts()
    icosahedron_hyper_edges = [
        HyperEdge(
            verts[i],
            verts[j],
            verts[k]
        ) for (i,j,k) in icosahedron_faces
    ]
    return icosahedron_hyper_edges
# split phi and theta

# vert coordinate from Icosahedron

# create verts from list

class SphereMesh:
    def __init__(self, R=1, symbolic=False):
        # verts:
        # a list for all vert id
        #  - node unique identifier
        #  - node index in list
        # map id to coordinate theta and phi
        #   use node property
        # map id to height
        self.R = R
        self.verts = getIcosahedronVerts(symbolic)
        self.isSymbolic = symbolic
        if symbolic:
            self.uniformSplitStep = self._uniformSplitStep
        else:
            self.uniformSplitStep = self._batchUniformSplitStep
        for i, vert in enumerate(self.verts):
            vert.idx = i
            vert.parentMesh = self
        # edges: all connected verts # TODO
        self._midpoints:Dict[Tuple[VertInfo,VertInfo], VertInfo] = {}
        # FIXME: use hashed set
        # a dictionary for edges and their midpoints
        # hyperEdges: all triangles
        self.hyperEdges = getIcosahedronFaces(self.verts)
        # containship graph
        # hyperEdges <-> verts inside (bipartite)
        # splitship graph
        # hyperEdge - child hyperEdges
        # lists for batch split
        # a list for hyperEdges each batch of split

    def midPoint(self,a,b) -> VertInfo:
        return self._midpoints[(a,b)]

    def getHeight(self, idx):
        return self.R  # FIXME

    def uniformSplit(self, iterations:int):
        iterations = int(iterations)
        for i in range(iterations):
            print("iter", i)
            self.uniformSplitStep()

    def _uniformSplitStep(self):
        # single step
        new_verts = []
        new_triangles = []
        for triangle in self.hyperEdges:
            # create midpoints
            for edge in triangle.edges:
                if edge not in self._midpoints:
                    point1, point2 = edge
                    midpoint = point1.getMidPoint(point2)
                    self._midpoints[(point1,point2)] = midpoint
                    self._midpoints[(point2,point1)] = midpoint
                    new_verts.append(midpoint)
            # add new triangles
            a,b,c = tuple(triangle)
            mab, mbc, mca = (
                self.midPoint(a,b), self.midPoint(b,c), self.midPoint(c,a)
            )
            children_triangles = [
                HyperEdge(a, mab, mca),
                HyperEdge(b, mab, mbc),
                HyperEdge(c, mca, mbc),
                HyperEdge(mab, mbc, mca)
            ]
            new_triangles += children_triangles
        for (i,vert) in enumerate(new_verts):
            vert.idx = i + len(self.verts)
        self.verts += new_verts
        self.hyperEdges += new_triangles

    def _batchUniformSplitStep(self):
        self.batchSplitStep(self.hyperEdges)

    def batchSplitStep(self, triangles:List[HyperEdge]):
        edges = set(sum(triangle.edges for triangle in triangles))
        edges = [
            edge for edge in list(edges) if edge not in self._midpoints
        ]
        # TODO: make it tensor
        edges_coord = torch.Tensor([
            [p1.theta,p1.phi,p2.theta,p2.phi]
            for p1,p2 in edges
        ])






    # method: retrieve a tensor for all verts theta and phi
    # mothod: retrieve a tensor for all verts heightmap (optional)

    # create a planet
    # split to N
    # then random sample (phi, theta, size, other param) x m as craters
    # for each crate
    # calculate distance from each hyperEdge
    # pooled_val(f, v1,v2,v3)
    #  ->  can use different kernel for this
    #  ->  use monotonicity if function

    # if close to ridge, the split

    # get splitted hyperEdges

    # calculate heightmap for each vert
    # given each crater

# TODO: implementation for batch height calculation

if __name__ == "__main__":
    # TODO: include which node belongs to which hyperEdge
    print(icosahedron_verts)
