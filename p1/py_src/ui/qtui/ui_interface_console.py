# -*- coding: utf-8-*-

from queue import Queue as PyQueue
from typing import Callable
# from panda3d.core import Vec3
from console.console import Console
from PyQt5.QtCore import Qt
from game.events import Events
from ui.qtui.managed_docks import ManagedDock
import argparse
from util.py_decorators import with_parser

def parser_sp():
    p = argparse.ArgumentParser(prog="sp", add_help=False)
    p.add_argument("dock_id")
    p.add_argument("new_dock_id")
    p.add_argument("--title", default="new-dock")
    p.add_argument("--split", choices=["v", "h"], default=None)
    p.add_argument("--pos",
        choices=["top","bottom","left","right"],
        default=None
    )    # --pos: default is None, 4 choices 
    return p 

# def parser_lscam():
def parser_show_df():
    p = argparse.ArgumentParser(prog="show-df", add_help=False)
    p.add_argument("dock_id")
    p.add_argument("df_name", nargs="?", default="widget_control")
    return p



def parser_show_camera():
    p = argparse.ArgumentParser(prog="show-camera", add_help=False)
    p.add_argument("dock_id")
    p.add_argument("camera_name")
    return p 


        # lscam
        # p = argparse.ArgumentParser(prog="lscam", add_help=False)
        # self.parsers["lscam"] = p
        
        # goto
        # p = argparse.ArgumentParser(prog="goto", add_help=False)
        # p.add_argument("widget_name")
        # self.parsers["goto"] = p
    




class MultiViewUIConsole(Console):
    def __init__(self, ui):
        super().__init__("multi-view-ui")
        self.ui = ui 
        self.command_dict = {
            "sp": (self.split_dock, "split dock, with dock id and new dock id"), # dock id, new dock id, new dock title, way of split(string, interpreted as qt split type when executed)
            "show-df": (self.show_df, "show dataframes"), # dock id to show; and which df to show (by string)
            # later put it into showbase console
            "lscam": (self.list_camera, "list all camera names that are in dict"), # no arg
            "show-camera": (self.show_camera, "show camera view on certain dock"), # dock id and camera name 
            "goto":(self.goto,"focus to certain widget"), # widget name; no need for argparse since it has only one arg
        }


    @with_parser(parser_sp())
    def split_dock(self, dock_id, new_dock_id, title, split=None, pos=None):
        # TODO: let help read doc
        """
        Split a dock widget and create a new dock.

        Default behavior:
        - If neither 'split' nor 'pos' is provided, a vertical split is used.
        - 'pos' can override 'split' to specify exact placement:
            - 'top' or 'left': new dock is above or left of the original dock.
            - 'bottom' or 'right': new dock is below or right of the original dock.
        - If only 'split' is provided:
            - 'v' or 'vertical' => vertical orientation.
            - 'h' or 'horizontal' => horizontal orientation.

        Parameters:
        - dock_id (str): ID of the existing dock to split.
        - new_dock_id (str): ID for the new dock.
        - title (str): Title of the new dock.
        - split (str, optional): 'v'/'vertical' or 'h'/'horizontal'.
        - pos (str, optional): 'top', 'bottom', 'left', 'right'.
        """
        dock = ManagedDock.get_object(dock_id)
        # FIXME: behavior when putting on left/top
        if dock is None:
            self.log(f"No dock named {dock_id}", "output")
            return

        new_dock = self.ui.create_dock(name=new_dock_id, title=title)
        if pos is None and split is None:
            pos = "bottom"
        if pos is not None and split is not None:
            if split in ["v","vertical"] and pos not in ["top","bottom"]:
                self.log("Invalid combination: vertical split cannot use left/right", "output")
                return

            if split in ["h","horizontal"] and pos not in ["left","right"]:
                self.log("Invalid combination: horizontal split cannot use top/bottom", "output")
                return
        if pos in ["top", "bottom"]:
            orientation = Qt.Vertical
        elif pos in ["left", "right"]:
            orientation = Qt.Horizontal
        elif split in ["v","vertical"]:
            orientation = Qt.Vertical
        else:
            orientation = Qt.Horizontal


        if pos == "top" or pos == "left":
            self.ui.splitDockWidget(new_dock, dock, orientation)
        else:
            self.ui.splitDockWidget(dock, new_dock, orientation)

        # self.ui.splitDockWidget(
            # dock,
            # new_dock,
            # Qt.Vertical if split.lower() in ["v", "vertical"] else Qt.Horizontal
        # )
        self.log(f"Dock {new_dock_id} created by splitting {dock_id}", "output")


    def goto(self, widget_name):
        widget = QPanda3DWidget.get_object(widget_name)
        if widget is None:
            self.log(f"No widget named {widget_name}", "output")
            return
        self.ui.setFocusWidget(widget)
        self.log(f"Focused widget {widget_name}", "output")

    @with_parser(parser_show_df())
    def show_df(self, dock_id, df_name):
        if df_name == "widget_control":
            dock = ManagedDock.get_object(dock_id)
            if dock:
                self.ui.show_widget_control_df(dock)
            else:
                self.log("dock not found:", dock_id)
        else:
            self.log("not implemented:",df_name)


    def list_camera(self, *args, **kwargs):
        self.log("not implemented: list_camera")

    @with_parser(parser_show_camera())
    def show_camera(self, *args, **kwargs):
        self.log("not implemented: show camera")
