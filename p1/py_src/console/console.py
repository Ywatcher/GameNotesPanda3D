from abc import ABC
from typing import (
    Callable, Dict, Iterable, 
    List, Optional, Union, Tuple
)
from queue import Queue as PyQueue
from direct.showbase.DirectObject import DirectObject
from util.log import Loggable
from game.events import Events


# TODO: console log place
# FIXME: command_dict: to command: func, doc

class Console(ABC, Loggable):

    def log(self, s: str, logtype="print"):
        if logtype == "output":
            self.out_buffer.put(s)
        elif logtype == "print":
            print(s)
        elif logtype == "log":
            self.log_buffer.put(s)
        else:
            raise NotImplementedError

    @property
    def command_list(self) -> List[str]:
        return list(self.command_dict.keys())

    @property
    def namespaced_command_list(self) -> List[str]:
        return [
            "{}::{}".format(self.namespace, cmd)
            for cmd in self.command_list
        ]

    def _help(self):
        # self.log(str(self.command_list), logtype="output")
        # TODO: with alias
        command_doc_lst = [
            "{}\t:{}".format(cmd, self.get_cmd_doc(cmd))
            for cmd in self.command_dict.keys()
        ]
        self.log("\n".join(command_doc_lst), logtype="output")

    @staticmethod
    def parse(console:"Console", s:str):
        # TODO: use ; to split commands
        # TODO: before that, need to deal with return values
        # TODO: kwargs
        fields = s.split()
        if len(fields) == 0:
            return
        console.his_buffer.put(s)
        namespaces_command = fields[0].split("::")
        command = namespaces_command[-1]
        if len(namespaces_command) == 2:
            namespace = namespaces_command[0] #TODO: more than 1 namespace
        elif len(namespaces_command) == 1:
            namespace = None
        else:
            # NotImplemented #TODO: log to console log
            return
        args = tuple(fields[1:])
        return console.execute(command, namespace, *args)

    def __init__(
        self, name:str, namespace:Optional[str]=None,
        is_local:bool=False
    ) -> None:
        self.name = name
        if namespace is None:
            self.namespace = name
        else:
            self.namespace = namespace
        self.is_local = is_local
        if not hasattr(self, "command_dict"):
            self.command_dict: Union[
                Dict[str, Union[Callable, Tuple[Callable, str]]],
                dict] =  {}
        self.out_buffer = PyQueue()
        self.log_buffer = PyQueue()
        self.his_buffer = PyQueue()

    def execute(self, command, namespace=None, *args, **kwargs):
        try:
            if (namespace is None and not self.is_local) \
                    or (namespace==self.namespace):
                cmd_func = self.get_cmd_func(command)
                ret = cmd_func(*args, **kwargs)
                return ret
            # else:
                # raise
        except Exception as e:
            self.log(str(e))

    def get_cmd_func(self, command):
        if command in self.command_dict:
            cmd_item = self.command_dict[command]
            if isinstance(cmd_item, Iterable):
                return cmd_item[0]
            elif isinstance(cmd_item, Callable):
                return cmd_item
            else:
                return lambda:None # TODO: raise error
        else:
            return lambda:None

    def get_cmd_doc(self, command):
        if command in self.command_dict:
            cmd_item = self.command_dict[command]
            if isinstance(cmd_item, Iterable):
                return cmd_item[1]
            elif isinstance(cmd_item, Callable):
                return str(cmd_item)
            else:
                return "..." # TODO: raise error
        else:
            return "..."

    @staticmethod
    def union(consoles:List["Console"], priority=None):
        return UnionConsole(consoles, priority)

    def lst_cmd(self):
        # list all commands
        # TODO: to output buffer
        self.log(str(self.command_dict.keys()))
        # TODO: log namespace\nall commands

    # def __add__(self, other):
        # if isinstance(other, Console):
            # return

class UnionConsole(Console):

    def __init__(
        self, consoles:List[Console], name:Optional[str]=None,
        namespace="global", # FIXME : what if a union whats to be local
        priority:Optional[list]=None
    ) -> None:
        consoles_sorted = consoles[::-1] #FIXME: use priority
        if name is None:
            name = "+".join([
                console.name for console in consoles
            ])
        super().__init__(name, namespace, is_local=False)
        self.namespaced_consoles:Dict[str, Console] = {}
        for console in consoles_sorted:
            # for non local consoles,
            # register their commands as my own commands
            # without namespaces
            if not console.is_local:
                self.command_dict.update(console.command_dict)
            if isinstance(console, UnionConsole):
                self.namespaced_consoles.update(console.namespaced_consoles)
            else:
                self.namespaced_consoles.update({console.namespace: console})

    def execute(self, command, namespace=None, *args, **kwargs):
        if namespace is None or namespace==self.namespace:
            return super().execute(command, namespace, *args, **kwargs)
        elif namespace in self.namespaced_consoles:
            return self.namespaced_consoles[namespace].execute(
                command, namespace, *args, **kwargs)

     #TODO
    # overwrite lst_cmd
