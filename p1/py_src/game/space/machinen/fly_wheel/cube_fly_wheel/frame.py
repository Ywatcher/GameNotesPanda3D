from typing import Dict
from panda3d.core  import (
    NodePath,
    Vec3
)
from panda3d.bullet import (
    BulletRigidBodyNode
)
from panda3d_game.game_object import  PhysicsGameObject
from util.bullet_geometry import *
from util.geometry import *
from art.basic import *

class FlyWheelFrame(PhysicsGameObject):
    
    def __init__(self, edge_length, edge_width, name:str, mass=1):
        PhysicsGameObject.__init__(self)
        self.name = "Frame.{}".format(name)
        self.edge_length = float(edge_length)
        self.edge_width = float(edge_width)
        self.mass = float(mass)
        self.geom_node = GeomNode(self.name)
        trape_edge = torch.Tensor([
            [-edge_length / 2, edge_length / 2, -edge_length / 2],
            [edge_length / 2, edge_length / 2, -edge_length / 2],
            [edge_length / 2 - edge_width, edge_length / 2 - edge_width, -edge_length / 2],
            [-edge_length / 2 + edge_width, edge_length / 2 - edge_width, -edge_length / 2]
        ])
        recta_edge = torch.Tensor([
            [-edge_length / 2 + edge_width, edge_length / 2 - edge_width, -edge_length / 2],
            [edge_length / 2 - edge_width, edge_length / 2 - edge_width, -edge_length / 2],
            [edge_length / 2 - edge_width, edge_length / 2 - edge_width, -edge_length / 2 + edge_width],
            [-edge_length / 2 + edge_width, edge_length / 2 - edge_width, -edge_length / 2 + edge_width],
        ])
        # first rotation
        transforms_1edge_to_1surf = [
                # xy
                torch.Tensor([
                    [0, 1, 0],
                    [-1, 0, 0],
                    [0, 0, 1]
                ]),
                torch.Tensor([
                    [-1, 0, 0],
                    [0, -1, 0],
                    [0, 0, 1]
                ]),
                torch.Tensor([
                    [0, -1, 0],
                    [1, 0, 0],
                    [0, 0, 1]
                ]),
                torch.Tensor([
                    [1, 0, 0],
                    [0, 1, 0],
                    [0, 0, 1]
                ])
            ]
        transforms_1surf_to_cube = [
                torch.Tensor([
                    [1, 0, 0],
                    [0, 1, 0],
                    [0, 0, 1]
                ]),
                # xz
                torch.Tensor([
                    [0, 0, 1],
                    [0, 1, 0],
                    [-1, 0, 0]
                ]),
                torch.Tensor([
                    [-1, 0, 0],
                    [0, 1, 0],
                    [0, 0, -1]
                ]),
                torch.Tensor([
                    [0, 0, -1],
                    [0, 1, 0],
                    [1, 0, 0]
                ]),
                # yz
                torch.Tensor([
                    [1, 0, 0],
                    [0, 0, -1],
                    [0, 1, 0]
                ]),
                torch.Tensor([
                    [1, 0, 0],
                    [0, 0, 1],
                    [0, -1, 0]
                ])
            ]
        trape_surf = batch_transform(
            [trape_edge], transforms_1edge_to_1surf)
        trape_cube = batch_transform(
            trape_surf, transforms_1surf_to_cube)
        recta_surf = batch_transform(
            [recta_edge], transforms_1edge_to_1surf)
        recta_cube = batch_transform(
            recta_surf, transforms_1surf_to_cube)
        self.faces = trape_cube + recta_cube
        self.geom = geom_frm_faces(name=self.name, faces=self.faces)
        self.geom_node.addGeom(self.geom)
        self.geom_np = NodePath(self.geom_node)
        self.rigid_node = BulletRigidBodyNode(self.name)
        self.rigid_node.setMass(self.mass)
        # FIXME: use minkowski sum
        for i in range(24):
            # print(i)
            convex_shape = BulletConvexHullShape()
            for point in trape_cube[i]:
                convex_shape.addPoint(Vec3(*point))
            for point in recta_cube[i]:
                convex_shape.addPoint(Vec3(*point))
            self.rigid_node.addShape(convex_shape)
        self.rigid_np = NodePath(self.rigid_node)
        self.geom_np.reparentTo(self.rigid_np)
        # marker nodes
        self.center_np = self.mainPath.attachNewNode("{}.center".format(self.name))
        self.center_np.setPos(0,0,0)
        # marker nodes for bearings
        self.bearings_np:Dict[str, NodePath] = createPosIndicatorNPth(
            self.mainPath,
            {
                "x+":(self.edge_length / 2 - self.edge_width, 0, 0),
                "x-":(-self.edge_length / 2 + self.edge_width, 0, 0),
                "y+":(0, self.edge_length / 2 - self.edge_width, 0),
                "y-":(0, -self.edge_length / 2 + self.edge_width, 0),
                "z+":(0, 0, self.edge_length / 2 - self.edge_width),
                "z-":(0, 0, -self.edge_length / 2 + self.edge_width)
            },
            node_name_prefix="{}.".format(self.name)
        )
        self.rigid_node.setLinearSleepThreshold(0)
        self.rigid_node.setAngularSleepThreshold(0)
        # print(self.rolling_bearings())
    
    def rolling_bearings(self):
        return {
            key: self.bearings_np[key].getPos() - self.mainPath.getPos()
            for key in self.bearings_np
        }