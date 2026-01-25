# -*- coding: utf-8-*-

from direct.showbase.ShowBase import ShowBase
from panda3d_game.app import ContextShowBase
from direct.task import Task
from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GeomEnums
)
import numpy as np
import torch
from art.basic import create_sphere_node, create_cube_node,uv_curve_surface
import builtins


class MyApp(ContextShowBase):
    def __init__(self):
        super().__init__()

        # cube = create_cube()
        sphere = create_sphere_node("01", 4, 4)
        self.render.attachNewNode(sphere)

        # Set the camera position
        # https://docs.panda3d.org/1.10/python/introduction/tutorial/controlling-the-camera
        self.taskMgr.add(self.spin_camera_task, "SpinCameraTask")

    def spin_camera_task(self, task):
        angleDegrees = task.time * 60.0
        angleRadians = angleDegrees * (np.pi / 180.0)
        self.camera.setPos(
            20 * np.sin(angleRadians), -20 * np.cos(angleRadians), 3)
        self.camera.setHpr(angleDegrees, 0, 0)

        return Task.cont


if __name__ == "__main__":
    import traceback
    try:
        with MyApp() as app:
            app.run()
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    finally:
        if hasattr(builtins, 'base'):
            builtins.base.destroy()















