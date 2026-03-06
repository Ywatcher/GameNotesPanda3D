from panda3d_game.input_source import ScreenRegionInput
from PyQt5.QtCore import QRect

class QWidgetScreenRegion(ScreenRegionInput):
    def __init__(self, widget):
        self.widget = widget

    def getW(self):
        return self.widget.width()

    def getH(self):
        return self.widget.height()

    def getPos(self):
        # map top-left to global coordinates
        top_left = self.widget.mapToGlobal(self.widget.rect().topLeft())
        return (top_left.x(), top_left.y())
