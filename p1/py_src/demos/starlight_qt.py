from typing import Tuple
from typing import List,Set, List, Dict,Callable
from panda3d_game.app import ControlShowBase, ContextShowBase, PhysicsShowBase,UniversalGravitySpace
from vispyutil.canvas import SynchronizedCanvas
from vispyutil.showbase import CanvasBackgroundShowBase

import numpy as np
from sympy.physics.units import (
    kilometer, meter,centimeter,
    gram, kilogram, tonne,
    newton, second
)
from panda3d.core import (
    NodePath,
    WindowProperties,
    Vec3,
    TextNode,
    PNMImage, Texture,
    CardMaker,Point2,
    NodePath, Camera, PerspectiveLens,
    Point3, LVector3f
)
from util.physics import autocomplete_units, G_val, getG
from demos.ball_room import MassedBall,tmoon
from util.log import *
from config.style import styleSheet
import yaml
from util.physics import autocomplete_units, G_val, getG
from art.assets.starfield import StarCanvas


class StarScene(CanvasBackgroundShowBase):
    def __init__(self):
        self.stars_canvas = StarCanvas(60000)
        CanvasBackgroundShowBase.__init__(self,self.stars_canvas)

class PlanetStarScene(
    StarScene,
    UniversalGravitySpace):

    def __init__(self):
        StarScene.__init__(self)
        unit = {
            "mass" : tonne,
            "length" : 100*meter,
            "time": 1 * second,
            # "force" : sp.Number(1e3) * newton
        }
        G_game = 0.001
        UniversalGravitySpace.__init__(
            self, unit=unit, G_val=G_game)
        self.planet1 = MassedBall(
            name="planet1",
            radius=100*meter,
            mass=1e6*tonne,
            units=self.unit
        )
        self.planet1.reparentTo(self.render)
        self.planet2 = MassedBall(
            name="planet2",
            radius=100*meter,
            mass=1e6*tonne,
            units=self.unit
        )
        self.planet2.reparentTo(self.render)
        self.planet1.set_texture(tmoon)
        self.planet2.set_texture(tmoon)
        self.planet1.setScale(1)
        self.planet1.setPos(0,5,0)
        self.planet2.setScale(1)
        self.planet2.setPos(0,-5,0)
        self.planet1.toBulletWorld(self.bullet_world)
        self.planet2.toBulletWorld(self.bullet_world)
        self.gravitational_bodies = [self.planet1, self.planet2]
        self.objects.update({
            "planet1":self.planet1,
            "planet2":self.planet2
        })
        self.accept('p', self.pause_switch)
        self.planet1.set_linear_velocity(Vec3(0,0,2))
        self.planet2.set_linear_velocity(Vec3(0,0,-2))
        # set velocity
    # todo; set initial state; back to initial state

    def potential(self):
        pass

# from
class PlanetStarScene_(StarScene,PhysicsShowBase):
    def __init__(self):
        StarScene.__init__(self)
        PhysicsShowBase.__init__(self)
        self.bullet_world.setGravity((0,0,0))
        self.unit = {
            "mass" : tonne,
            "length" : 100*meter,
            "time": 1 * second,
            # "force" : sp.Number(1e3) * newton
        }
        autocomplete_units(self.unit)
        # self.planet1 = MassedBall(
        #     name="planet1",
        #     radius=1000*meter,
        #     mass=1e6*tonne,
        #     units=self.unit
        # )
        from art.basic import create_cylinder_node, create_sphere_node
        self.cld = create_sphere_node(
            "cld",lat_res=12,lon_res=12,
            interior=True
        )
        self.cld_npth = self.rdr_scene.attachNewNode(self.cld)
        self.cld_npth.set_texture(tmoon)
        # self.planet1.reparentTo(self.render)
        # self.planet1.set_texture(tmoon)
        # self.planet1.setScale(10)
        # self.planet1.setPos(0,10,0)


from qpanda3d import QShowBase, QPanda3DWidget, QControl, Synchronizer
class PlanetStarSpace(PlanetStarScene, QControl):
    def __init__(self, isQt = True):
        import pdb
        QControl.__init__(self)
        PlanetStarScene.__init__(self)
        self.isQt = isQt
        if self.isQt:
            self.startQt()
from demos.physics_room import PhyscRoomConsole
from ui.qtui import *

class SpaceGame(RawQtGUI):
    def get_game(self):
        return PlanetStarSpace()

    def get_console(self):
        return PhyscRoomConsole(showbase=self.panda3d)

if __name__ == '__main__':
    # torch.set_printoptions(precision=16, sci_mode=False)
    import sys
    app = QApplication(sys.argv)
    window = SpaceGame()
    window.show()
    sys.exit(app.exec_())
