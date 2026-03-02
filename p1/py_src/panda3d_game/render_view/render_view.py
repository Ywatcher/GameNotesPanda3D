from panda3d.core import (
        Camera
        )


class RenderView:
    def __init__(self, main_camera: Camera = None, view_manager:"ViewManager" = None):
    
        self.camera_list = {} # TODO: use setter and getter
        self.buffer_list = {}
        self._isActive = True 
        self.camera_list["main_camera"] = main_camera
        self.view_manager = view_manager


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

    @property
    def main_camera(self):
        return self.camera_list["main_camera"]


    def getCamera(self, name):
        if name in self.camera_list:
            return self.camera_list[name]


    def setPos(self, *args):
        self.main_camera.setPos(*args)

    def setHpr(self, *args):
        self.main_camera.setHpr(*args)

    def setH(self, *args):
        self.main_camera.setH(*args)

    def setP(self, *args):
        self.main_camera.setP(*args)

    def setR(self, *args):
        self.main_camera.setR(*args)

    def setZ(self, *args):
        self.main_camera.setZ(*args)

    def getQuat(self, *args):
        return self.main_camera.getQuat(*args)

    def getPos(self, *args):
        return self.main_camera.getPos(*args)

    def getZ(self, *args):
        return self.main_camera.getZ(*args)


    


class RenderViewManager:
    def __init__(self, showbase):
        self.showbase = showbase
        # TODO: a range of views 
        # 
         




    










