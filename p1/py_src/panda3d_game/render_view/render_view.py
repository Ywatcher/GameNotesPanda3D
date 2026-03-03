from typing import Dict,Union


from panda3d.core import (
        Camera
        )

from panda3d.core import (
    GraphicsOutput, Texture,
    ConfigVariableManager, WindowProperties,
    LVecBase4f, FrameBufferProperties,
    GraphicsPipe
)
from util.py_decorators import forward_methods_to
from .camera_attributes import forwarded_methods

@forward_methods_to("main_camera", forwarded_methods)
class RenderView:
    def __init__(self, mount_camera: Camera, view_manager:"ViewManager" = None, name=None,

        size=1.0,
         clear_color=LVecBase4f(0.1, 0.1, 0.1, 1),
        # parent=None 
        ):
        self.name = name 
        self.clear_color = clear_color 
        assert isinstance(mount_camera, Camera)
        self._mounted_camera = mount_camera
        self.camera_list = {"main":None} # TODO: use setter and getter
        self.buffer_list = {"main":None}
        self.view_manager:"ViewManager" = view_manager
        self.screenTexture = Texture()
        self._isStarted = False
        self._isActive = True  # FIXME
        # self.parent = parent # showbase, change it to a factory then TODO

    # ====
    # put into factory
    @property
    def parent(self): # remove in future
        return self.view_manager.showbase

    # getAspectRatio TODO 
    
    # def getAspectRatio(self, win = None): do I really need this? 
        
        # if win is None and hasattr(self, 'parent') and self.parent is not None:
            # return float(self.parent.width()) / float(self.parent.height())
        # else:
            # return super().getAspectRatio(win)

    @property
    def win(self):
        return self.parent.win # FIXME

    @property 
    def graphicsEngine(self):
        return self.parent.graphicsEngine

    @property
    def pipe(self):
        return self.parent.pipe

    def start(self):
        # FIXME what if put it before creating game assets
        if not self._isStarted:
            clear_color = self.clear_color
            name = self.name
            size = self.size
            sort = -100
            self.screenTexture.setMinfilter(Texture.FTLinear)
            
            self.screenTexture.setFormat(Texture.FRgba32)
            self.screenTexture.set_wrap_u(Texture.WM_clamp)
            self.screenTexture.set_wrap_v(Texture.WM_clamp)
            # FIXME: put into factory
            buff_size_x = int(self.win.get_x_size() * size)
            buff_size_y = int(self.win.get_y_size() * size)
            winprops = WindowProperties()
            winprops.set_size(buff_size_x, buff_size_y)

            props = FrameBufferProperties()
            props.set_rgb_color(True)
            props.set_rgba_bits(8, 8, 8, 8)
            props.set_depth_bits(8)
            
            self.main_buffer = self.graphicsEngine.make_output(
                self.pipe, name, sort,
                props, winprops,
                GraphicsPipe.BF_resizeable,
                self.win.get_gsg(), self.win) 

            self.main_buffer.addRenderTexture(
                self.screenTexture, GraphicsOutput.RTMCopyRam)
            self.main_buffer.set_sort(sort)
            self.main_camera = self.makeCamera(self.buff)
            self.reparentTo(self._mounted_camera)
            # self.camNode = self.cam.node()
            # self.camLens = self.camNode.get_lens()
            if clear_color is None:
                self.main_buffer.set_clear_active(GraphicsOutput.RTPColor, False)
            else:
                self.main_buffer.set_clear_color(clear_color)
                self.main_buffer.set_clear_active(GraphicsOutput.RTPColor, True)
            # self.movePointer = self.empty
            self._isQtStart = True



    # TODO:
    # in QWidget,
    # resize is implemented by resizing the main buffer. 
    # in future, we put them here -- when there are multiple buffers each view

    def cursor_in(): # FIXME
        pass 

    def cursor_out():
        pass

    @property
    def camNode(self):
        return self.main_camera.node()

    @property
    def camLens(self):
        return self.camNode.get_lens()

    def get_lens():
        return self.main_camera.node().get_lens()

    def mount_to(self,camera:Camera):
        # FIXME: keep properties of camera updated
        self._mounted_camera = camera
        if self._isStarted:
            self.main_camera.reparentTo(camera)

    @property
    def mounted_camera(self):
        return self._mounted_camera

    @property
    def main_camera(self):
        return self.camera_list["main"]

    @main_camera.setter 
    def main_camera(self, cam):
        self.camera_list["main"] = cam

    @property
    def main_buffer(self):
        return self.buffer_list["main"]

    @property 
    def main_buffer(self, buf):
        self.buffer_list["main"] = buf

    @property
    def screenTexture(self):
        pass

    def getID(self):
        pass


    def setActive(self):
        self._isActive = True 

    def isActive(self):
        return self._isActive 


    def registerCamera(self, name, camera):
        if name not in self.camera_list:
            self.camera_list[name] = camera
        else:
            pass 

    def createCamera(self, name):
        pass 



    def getCamera(self, name):
        if name in self.camera_list:
            return self.camera_list[name]
    


class RenderViewManager:
    def __init__(self, showbase):
        self.showbase = showbase
        # map id of camera to its view 
        self.views:Dict[int, RenderView] = {}

    def createViewForCamera(self, camera: Union[int, Camera],name=None):
        if isinstance(camera, Camera):
            camera = id(camera)
        # FIXME:
        # if is string -> int 
        # and assert the obj with this id is a Camera
        view = RenderView(mount_camera=camera, view_manager=self,name=name)
        self.views[camera] = view 
        return view

    # TODO: manage life span
        # TODO: a range of views 
        # 
         




    










