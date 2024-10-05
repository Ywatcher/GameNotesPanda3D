import sys
from vispy import app, scene, visuals, use
import numpy as np
from vispy.visuals.transforms.linear import MatrixTransform
import traceback
try:
    use('glfw')
except Exception as e:
    print(e)
    print(traceback.format_exc())
    raise(e)
    pass
from vispyutil.scene import UnboundedTurnableCam

class SynchronizedCanvas(scene.SceneCanvas):
    def __init__(self):
        scene.SceneCanvas.__init__(
            self,
            keys='interactive',
            show=False,
        )
        self.unfreeze()
        # Set up a viewbox to display camera
        self.view = self.central_widget.add_view()
        # Compared to vispy.scene.TurnableCamera,
        # this camera is unbounded in elevation axis
        # which agrees with panda3d
        self.view.camera = UnboundedTurnableCam()
        self.view.camera.set_range()

    def update_camera(self, mat: np.ndarray, fov=None, aspect=None):
        self.view.camera._set_scene_transform(MatrixTransform(
            mat
        ))
        self.view.camera.view_changed()
        # self.view.camera.orbit(1,0)
        if fov is not None:
            self.view.camera.fov=fov
        if aspect is not None:
            self.view.camera.aspect = aspect
        self.update()

    def update_camera_hpr(self, h=0,p=0,r=0,fov=None, aspect=None):
        self.view.camera.azimuth = h
        self.view.camera.elevation = p
        self.view.camera.roll = r
        if fov is not None:
            self.view.camera.fov=fov
        if aspect is not None:
            self.view.camera.aspect = aspect
        self.update()
