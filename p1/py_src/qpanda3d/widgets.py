# -*- coding: utf-8-*-
"""
Module : QPanda3DWidget
Author : Saifeddine ALOUI
Description :
    This is the QWidget to be inserted in your standard PyQt5 application.
    It takes a Panda3DWorld object at init time.
    You should first create the Panda3DWorkd object before creating this widget.
"""
# PyQt imports
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# Panda imports
import builtins
from panda3d.core import loadPrcFileData, Texture 

from QPanda3D.QPanda3D_Buttons_Translation import QPanda3D_Button_translation
from QPanda3D.QPanda3D_Keys_Translation import QPanda3D_Key_translation
from QPanda3D.QPanda3D_Modifiers_Translation import QPanda3D_Modifier_translation

from qtutil.qobserver import *
from qtutil.event import *

__all__ = ["QPanda3DWidget", "Synchronizer"]

class Synchronizer(QTimer):

    def __init__(self, FPS=60):
        QTimer.__init__(self)
        dt = 1000 // FPS
        self.setInterval(int(round(dt)))
        self.timeout.connect(self.tick)
        self.showbase = [] # it should have only one member
        self.widgets = []

    def addWidget(self, widget):
        self.widgets.append(widget)

    def setShowBase(self,  showbase):
        assert hasattr(showbase, "taskMgr")
        self.showbase.append(showbase)

    def tick(self):
        # print(self.showbase)
        if len(self.showbase)>0:
            self.showbase[0].taskMgr.step()
            # self.showbsae.taskMgr.step()
        for widget in self.widgets:
            # print(widget.mapToGlobal(QPoint(0, 0)))
            widget.update()


# TODO: handle key press and mouse move together



def get_panda_key_modifiers(evt):
    panda_mods = []
    qt_mods = evt.modifiers()
    for qt_mod, panda_mod in QPanda3D_Modifier_translation.items():
        if (qt_mods & qt_mod) == qt_mod:
            panda_mods.append(panda_mod)
    return panda_mods


def get_panda_key_modifiers_prefix(evt):
        # join all modifiers (except NoModifier, which is None) with '-'
    mods = [mod for mod in get_panda_key_modifiers(evt) if mod is not None]
    prefix = "-".join(mods)

    # Fix the case where the modifier key is pressed
    # alone without other things
    # if not things like control-control would be possible
    if isinstance(evt, QtGui.QMouseEvent):
        key = QPanda3D_Button_translation[evt.button()]
    elif isinstance(evt, QtGui.QKeyEvent):
        key = QPanda3D_Key_translation[evt.key()]
    elif isinstance(evt, QtGui.QWheelEvent):
        key = "wheel"
    else:
        raise NotImplementedError("Unknown event type")

    if key in mods:
        mods.remove(key)
        prefix = "-".join(mods)

    # if the prefix is not empty, append a '-'
    if prefix == "-":
        prefix = ""
    if prefix:
        prefix += "-"

    return prefix
class QPanda3DWidget(QWidget, QObserved):
    """
    An interactive panda3D QWidget
    Parent : Parent QT Widget
    FPS : Number of frames per socond to refresh the screen
    debug: Switch printing key events to console on/off
    """

    def __init__(
        self, panda3DWorld, parent=None, FPS=60, debug=False,
        synchronizer=None
    ):
        QWidget.__init__(self, parent)
        QObserved.__init__(self)

        # set fixed geometry
        self.panda3DWorld = panda3DWorld
        self.panda3DWorld.set_parent(self)
        # Setup a timer in Qt that runs taskMgr.step() to simulate Panda's own main loop
        # pandaTimer = QTimer(self)
        # pandaTimer.timeout.connect()
        # pandaTimer.start(0)

        self.setFocusPolicy(Qt.StrongFocus)

        # Setup another timer that redraws this widget in a specific FPS
        # redrawTimer = QTimer(self)
        # redrawTimer.timeout.connect(self.update)
        # redrawTimer.start(1000/FPS)

        self.paintSurface = QPainter()
        self.rotate = QTransform()
        self.rotate.rotate(180)
        self.out_image = QImage()

        size = self.panda3DWorld.cam.node().get_lens().get_film_size()
        self.initial_film_size = QSizeF(size.x, size.y)
        self.initial_size = self.size()

        # if synchronizer is None:
        #     self.synchronizer = QPanda3DSynchronizer(self, FPS)
        # else:
        #     self.synchronizer = synchronizer
        # if not self.synchronizer.isActive():
        #     self.synchronizer.start()

        self.debug = debug

    def mousePressEvent(self, evt):
        button = evt.button()
        try:
            b = f"{get_panda_key_modifiers_prefix(evt)}{QPanda3D_Button_translation[button]}"
            if self.debug:
                print(b)
            messenger.send(b,[{"x":evt.x(),"y":evt.y()}])
        except Exception as e:
            print("Unimplemented button. Please send an issue on github to fix this problem")
            print(e)

    def mouseMoveEvent(self, evt:QtGui.QMouseEvent):
        button = evt.button()
        try:
            b = "mouse-move"
            if self.debug:
                print(b)
            messenger.send(b,[{"x":evt.x(),"y":evt.y()}])
        except Exception as e:
            print("Unimplemented button. Please send an issue on github to fix this problem")
            print(e)

    def mouseReleaseEvent(self, evt):
        button = evt.button()
        try:
            b = f"{get_panda_key_modifiers_prefix(evt)}{QPanda3D_Button_translation[button]}-up"
            if self.debug:
                print(b)
            messenger.send(b,[{"x":evt.x(),"y":evt.y()}])
        except Exception as e:
            print("Unimplemented button. Please send an issue on github to fix this problem")
            print(e)

    def wheelEvent(self, evt):
        delta = evt.angleDelta().y()
        try:
            w = f"{get_panda_key_modifiers_prefix(evt)}wheel"
            if self.debug:
                print(f"{w} {delta}")
            messenger.send(w, [{"delta": delta}])
        except Exception as e:
            print("Unimplemented button. Please send an issue on github to fix this problem")
            print(e)

    def keyPressEvent(self, evt):
        key = evt.key()
        if key==ord(':'):
            evt_to_cmd = QEvent(FOCUS_CONSOLE)
            self.send_qevent(evt_to_cmd)
        try:
            k = f"{get_panda_key_modifiers_prefix(evt)}{QPanda3D_Key_translation[key]}"
            if self.debug:
                print(k)
            messenger.send(k)
            # FIXME: if k in the list that can be sent
            messenger.send('button', [k])
        except Exception as e:
            print("Unimplemented key. Please send an issue on github to fix this problem")
            print(e)

    def keyReleaseEvent(self, evt):
        key = evt.key()
        # print(evt.nativeScanCode())
        try:
            k = f"{get_panda_key_modifiers_prefix(evt)}{QPanda3D_Key_translation[key]}-up"
            if self.debug:
                print(k)
            messenger.send(k)
            # FIXME:
            messenger.send('button-up', [k.strip('-up')])
        except Exception as e:
            print("Unimplemented key. Please send an issue on github to fix this problem")
            print(e)

    def resizeEvent(self, evt):
        lens = self.panda3DWorld.cam.node().get_lens()
        lens.set_film_size(
            self.initial_film_size.width() * evt.size().width()
            / self.initial_size.width(),
            self.initial_film_size.height() * evt.size().height()
            / self.initial_size.height()
        )
        self.panda3DWorld.buff.setSize(evt.size().width(), evt.size().height())

    def minimumSizeHint(self):
        return QSize(400, 300)

    # Use the paint event to pull the contents of the panda texture to the widget
    def paintEvent(self, event):
        if self.panda3DWorld.screenTexture.mightHaveRamImage():
            self.panda3DWorld.screenTexture.setFormat(Texture.FRgba32)
            data = self.panda3DWorld.screenTexture.getRamImage().getData()
            img = QImage(
                data, self.panda3DWorld.screenTexture.getXSize(), 
                self.panda3DWorld.screenTexture.getYSize(),
                QImage.Format_ARGB32
            ).mirrored()
            self.paintSurface.begin(self)
            self.paintSurface.drawImage(0, 0, img)
            self.paintSurface.end()

    def movePointer(self, device, x, y):
        # Get the global position of the widget (top-left corner)
        widget_pos = self.mapToGlobal(QPoint(0, 0))
        global_x = widget_pos.x() + int(x)
        global_y = widget_pos.y() + int(y)
        #TODO: multi device
        QCursor.setPos(global_x,global_y)

    # TODO:
    # requestProperties
    def showCursor(self):
        self.setCursor(QCursor(Qt.ArrowCursor))

    def hideCursor(self):
        self.setCursor(QCursor(Qt.BlankCursor))

    def setFocus(self, cursor_in=True):
        QWidget.setFocus(self)
        if cursor_in:
            self.panda3DWorld.cursor_in()

    

    
    # def update_camera_tmp(self, task):
    #     """updata camera to follow mouse movement"""
    #     if self.mouseWatcherNode.hasMouse() and self.is_cursor_in_game:
    #         # get mouse position (unified to range(-1,1))
    #         mouse_x, mouse_y = self.getMouseXY() #FIXME
    #         # calculate the shift of the mouse
    #         delta_x = mouse_x - self.prev_mouse_x
    #         delta_y = mouse_y - self.prev_mouse_y

    #         # 调整摄像机的水平旋转和俯仰角度
    #         camera_h = self.display_camera.getH() - delta_x * 0.1
    #         camera_p = self.display_camera.getP() - delta_y * 0.1

    #         # 设置新的摄像机角度
    #         self.display_camera.setH(camera_h)
    #         self.display_camera.setP(camera_p)

    #         # 将鼠标指针重置到窗口的中心
    #         self.center_mouse()
    #     return task.cont