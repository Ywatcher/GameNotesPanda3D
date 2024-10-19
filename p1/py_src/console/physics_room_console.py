# -*- coding: utf-8-*-

from queue import Queue as PyQueue
from typing import Callable
from panda3d.core import Vec3
from console.console import Console
from panda3d_game.app import UniversalGravitySpace, PhysicsShowBase
from panda3d_game.game_object import GameObject
from game.events import Events



class PhyscRoomConsole(Console):
    # print as output
    def __init__(self, showbase:PhysicsShowBase) -> None:
        super().__init__(name="physics_room", namespace="room")
        self.showbase = showbase
        self.command_dict = {
            "h": (self._help, "print help"),
            "quit":(self.end_game, "end game"),
            "ls":(self.lst_objs, "list accessible objects"),
            "sel": (self.sel_obj, "select objs"),
            "setv": (self.set_v, "set linear velocity"),
            "setp": (self.set_p, "set pos"),
            "p":(self.showbase.pause_switch, "pause or resume")
        }
        if isinstance(showbase, UniversalGravitySpace):
            self.command_dict.update({
                "setG":(self.showbase.set_G_game, "set gravity constant"),
            })
        self._end_interface:Callable = lambda:None
        # self.objects:Dict[str, Union[NodePath, GameObject]]
        self.messageq = PyQueue()
        self.curr_objs = []  # currently selected objs

    @property
    def objects(self):
        return self.showbase.objects

    # def log(self, s: str, logtype="print"):
        # # TODO: put to buffer
        # print(s)

    # commands
    def lst_objs(self, *args):
        self.log(
            str(self.showbase.objects),
            "output"
        )

    def sel_obj(self, *args):
        # TODO: kwargs, unionmode = True
        if len(args)>0:
            objs_selected = [
                s for s in args if s in self.showbase.objects.keys()
            ]
            obj_omitted = [
                s for s in args if s not in self.showbase.objects.keys()
            ]
            if len(objs_selected)>0:
                self.curr_objs = objs_selected
                self.log(
                    "selected objs: {}".format(self.curr_objs),
                    "output"
                )
            else:
                self.log(
                    "no valid objs found, use dsel [obj] or dsel all "
                    + "to deselect objects",
                    "output"
                )
                self.log(
                    "not found in accessible objects: {}".format(obj_omitted),
                    "output"
                )

    def set_v(self, *args):
        # TODO:
        # add syntax: setv planet1=(1,0,0) planet2=(-1,0,0)
        try:
            vx = float(args[0])
            vy = float(args[1])
            vz = float(args[2])
            if len(args)>3:
                curr_objs = [
                    s for s in args[3:]
                    if s in self.showbase.objects
                ]
            else:
                curr_objs = self.curr_objs
            for s in curr_objs:
                obj = self.showbase.objects[s]
                if isinstance(obj, GameObject):
                    obj.set_linear_velocity(Vec3(vx,vy,vz))
                else:
                    raise NotImplementedError
        except Exception as e:
            self.log(str(e), "log")

    def set_p(self, *args):
        # TODO:
        # add syntax: setv planet1=(1,0,0) planet2=(-1,0,0)
        try:
            px = float(args[0])
            py = float(args[1])
            pz = float(args[2])
            if len(args)>3:
                curr_objs = [
                    s for s in args[3:]
                    if s in self.showbase.objects
                ]
            else:
                curr_objs = self.curr_objs
            for s in curr_objs:
                obj = self.showbase.objects[s]
                if isinstance(obj, GameObject):
                    obj.setPos(Vec3(px,py,pz))
                else:
                    raise NotImplementedError
        except Exception as e:
            self.log(str(e), "log")




    def end_game(self):
        # self.showbase.userExit()
        self.showbase.actionq.put(Events.GameEndEvent)
        self._end_interface()


