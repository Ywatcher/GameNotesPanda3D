# -*- coding: utf-8-*-

from queue import Queue as PyQueue
from typing import Callable
from panda3d.core import Vec3
from console.console import Console
from game.events import Events
from ui.qtui.managed_docks import ManagedDock
import argparse



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

    def _build_parsers(self):

        # sp
        p = argparse.ArgumentParser(prog="sp", add_help=False)
        p.add_argument("dock_id")
        p.add_argument("new_dock_id")
        p.add_argument("--title", default="new-dock")
        p.add_argument("--split", choices=["v", "h"], default="v")
        self.parsers["sp"] = p

        # show-df
        p = argparse.ArgumentParser(prog="show-df", add_help=False)
        p.add_argument("dock_id")
        p.add_argument("df_name",default="widget_control")
        self.parsers["show-df"] = p

        # lscam
        p = argparse.ArgumentParser(prog="lscam", add_help=False)
        self.parsers["lscam"] = p

        # show-camera
        p = argparse.ArgumentParser(prog="show-camera", add_help=False)
        p.add_argument("dock_id")
        p.add_argument("camera_name")
        self.parsers["show-camera"] = p

        # goto
        # p = argparse.ArgumentParser(prog="goto", add_help=False)
        # p.add_argument("widget_name")
        # self.parsers["goto"] = p

    def split_dock(self, dock_name, new_name, title, split_type):
        dock = ManagedDock.get_object(dock_name)
        if dock is None:
            self.log(f"No dock named {dock_name}", "output")
            return

        new_dock = self.ui.create_dock(name=new_name, title=title)
        self.ui.splitDockWidget(
            dock,
            new_dock,
            Qt.Vertical if split_type.lower() in ["v", "vertical"] else Qt.Horizontal
        )
        self.log(f"Dock {new_name} created by splitting {dock_name}", "output")


    def goto(self, widget_name):
        widget = QPanda3DWidget.get_object(widget_name)
        if widget is None:
            self.log(f"No widget named {widget_name}", "output")
            return
        self.ui.setFocusWidget(widget)
        self.log(f"Focused widget {widget_name}", "output")

    def show_df(self, dock_id, df_name):
        if df_name == "widget_control":
            dock = ManagedDock.get_object(dock_id)
            if dock:
                self.ui.show_widget_control_df()
            else:
                self.log("dock not found:", dock_id)
        else:
            self.log("not implemented:",df_name)


    def list_camera(self, *args, **kwargs):
        self.log("not implemented: list_camera")

    def show_camera(self, *args, **kwargs):
        self.log("not implemented: show camera")
