from vispy import app
import numpy as np
from util.texture import np2texture, rgba_mpl2pd3d, texture_load_np
from panda3d_game.app.app_ import ContextShowBase
from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GeomEnums,
    NodePath,
    CardMaker,
    Texture,
    CardMaker,
    Point2,
    Vec3
)
from util.rendering import *
from vispyutil.scene import UnboundedTurnableCam
from vispyutil.canvas import SynchronizedCanvas


class CanvasBackgroundShowBase(ContextShowBase):
    def __init__(self, canvas: SynchronizedCanvas):
        # if not has
        ContextShowBase.__init__(self)
        # ControlShowBase.__init__(self)
        self.bg_canvas = canvas
        self.bg_canvas.app.run()
        self.bg_texture = Texture()
        self.bg_texture.set_wrap_u(Texture.WM_clamp)
        self.bg_texture.set_wrap_v(Texture.WM_clamp)
        self.bg_cm = CardMaker('bg')
        self.bg_cm.setFrame(-1,1,-1,1)
        self.bg_initial_width = 2
        self.bg_initial_height = 2
        self.bg_cm.setUvRange(Point2(0, 1),  # ll
                          Point2(1, 1),  # lr
                          Point2(1, 0),  # ur
                          Point2(0, 0))
        self.bg_plane_pth = self.display_camera.attach_new_node(self.bg_cm.generate())
        self.bg_near = 10
        top, right = self.bg_fit_lens()
        self.bg_plane_pth.setPos(0,self.bg_near,0)
        self.bg_plane_pth.setTexture(self.bg_texture)
        self.bg_plane_pth.setBin("background", SORT_BG)
        self.bg_plane_pth.setDepthTest(False)
        self.bg_plane_pth.setDepthWrite(False)

        self.taskMgr.add(self.updateBGTask)

    def updateBGTask(self, task):
        top, right = self.bg_fit_lens()
        self.stars_canvas.update_camera_hpr(
            self.display_camera.getH(),
            -self.display_camera.getP(),
            self.display_camera.getR(),
        )
        stars = self.bg_canvas.render()
        texture_load_np(self.bg_texture, stars, format_=Texture.F_rgba)
        return task.cont

    def bg_fit_lens(self):
        lens = self.camLens
        fov_rad = lens.getFov() * (np.pi/180)
        # aspect_ratio = lens.getAspectRatio()
        top = self.bg_near * np.tan(fov_rad[1]/2)*2
        right = self.bg_near * np.tan(fov_rad[0]/2)*2
        scale = max(top/self.bg_initial_height, right/self.bg_initial_width)
        self.bg_plane_pth.setScale(scale,1,scale)
        return top, right
