# -*- coding: utf-8-*-

from abc import ABC
from typing import (
    Callable, Dict, Iterable,
    List, Optional, Union, Tuple
)
import argparse
from queue import Queue as PyQueue
from direct.showbase.DirectObject import DirectObject
from util.log import Loggable
from game.events import Events


# TODO: console log place
# FIXME: command_dict: to command: func, doc

class Console(ABC, Loggable):
    """
    cmd styled console
    """

    def log(self, s: str, logtype="print"):
        if logtype == "output":
            self.out_buffer.put(s)
        else:
            super().log(s, logtype)
        # elif logtype == "print":
        #     print(s)
        # elif logtype == "log":
        #     self.log_buffer.put(s)
        # else:
        #     raise NotImplementedError

    def get_namespace(self,cmd):
        l = cmd.split("::")
        if len(l)==2:
            return l[0], l[1]
        elif len(l) == 1:
            return None, l[0]
        else:
            return NotImplemented
        

    @property
    def command_list(self) -> List[str]:
        return list(self.command_dict.keys())

    @property
    def namespaced_command_list(self) -> List[str]:
        return [
            "{}::{}".format(self.namespace, cmd)
            for cmd in self.command_list
        ]

    def _help(self, cmd_name:str=None):
        if cmd_name:
            if cmd_name in self.command_dict:
                func, doc = self.command_dict[cmd_name]
                self.log(f"{cmd_name} : {doc}", logtype="output")
                parser = getattr(func, "_argparser", None)
                if parser:
                    self.log(parser.format_help(), logtype="output")
                return
            else: 
                self.log(f"No help found for command '{cmd_name}'", logtype="output")
                return
        # self.log(str(self.command_list), logtype="output")
        # TODO: with alias
        command_doc_lst = [
            "{}\t:{}".format(cmd, self.get_cmd_doc(cmd))
            for cmd in self.command_dict.keys()
        ]
        self.log("\n".join(command_doc_lst), logtype="output")

    # def _help_func_on_dict(self, cmd_name, cmd_dict):


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
        return console.execute(command, namespace, False,*args)

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
            self.command_dict: Dict[
                    str, 
                    Union[Callable, Tuple[Callable, str]]
            ]  =  {}
        self.out_buffer = PyQueue()
        self.log_buffer = PyQueue()
        self.his_buffer = PyQueue()


    def execute(self, command, namespace=None, parsed=False, *args, **kwargs):
        try:
            if (namespace is None and not self.is_local) \
                    or (namespace==self.namespace):
                cmd_func = self.get_cmd_func(command)
                # parser = self.get_cmd_parser(command)
                parser = getattr(cmd_func, "_argparser", None)
                if parser is not None and not parsed:
                    parsed_args = parser.parse_args(list(args))
                    kwargs = vars(parsed_args)
                    args = ()
                ret = cmd_func(*args, **kwargs)
                return ret
            # else:
                # raise
        except TypeError as type_error:
            self.log(str(type_error))
            print("arg",args)
            print("kwargs",kwargs)
            import traceback
            traceback.print_exc()
        except Exception as e:
            self.log(str(e))
            import traceback
            traceback.print_exc()

    def get_cmd_parser(self, command) -> Optional[argparse.ArgumentParser]:
        return self.parsers.get(command)


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
# TODO: flat union console, for consoles with same name space


class UnionConsole(Console):

    def __init__(
        self, consoles:List[Console], name:Optional[str]=None,
        namespace="global", # FIXME : what if a union whats to be local
        priority:Optional[list]=None
    ) -> None:
        flat_consoles = []
        for c in consoles:
            if isinstance(c, UnionConsole) and c.namespace == namespace:
                # namespace 相同的 UnionConsole 展开
                flat_consoles.extend(c.namespaced_consoles.values())
            else:
                flat_consoles.append(c)
        if priority is not None:
            consoles_sorted = sorted(
                flat_consoles,
                key=lambda c: priority.index(c.name) if c.name in priority else len(priority)
            )
        else:
            consoles_sorted = flat_consoles[::-1]

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
                # FIXME: flat union console 
                self.namespaced_consoles.update({console.namespace: console})
        self.command_dict.update({
            "h": (self._help, "print help")
            })
        for ns, console in self.namespaced_consoles.items():
            orig_log = console.log
            def proxy_log(s, logtype="print", _orig=orig_log):
                return self.log(s, logtype)
            console.log = proxy_log


    def execute(self, command, namespace=None, *args, **kwargs):
        if namespace is None or namespace==self.namespace:
            return super().execute(command, namespace, *args, **kwargs)
        elif namespace in self.namespaced_consoles:
            return self.namespaced_consoles[namespace].execute(
                command, namespace, *args, **kwargs)
        else:
            self.log(f"Command '{command}' not found in namespace '{namespace}'")
            return None

     #TODO
    # overwrite lst_cmd
    def _help(self,cmd: Optional[str] = None):
        """
        重载 help：默认打印每个子 console 的 help。
        """

        if cmd is not None: 
            namespace, cmd_name = self.get_namespace(cmd)
            namespace_console = None
            if namespace is None or not self.namespaced_consoles:
                # with no namespace
                title = cmd_name
                cmd_dict = self.command_dict
            elif namespace not in self.namespaced_consoles:
                # namespace not found
                title = f"namespace:{namespace} not found; \n{cmd_name}"
                cmd_dict = self.command_dict
            else:
                # has correct namespace
                title = f"{namespace}::{cmd_name}"
                cmd_dict = self.namespaced_consoles[namespace].command_dict
                namespace_console = self.namespaced_consoles[namespace]
            self.log(title, logtype="output")
            if cmd_name in cmd_dict:
                func, doc = cmd_dict[cmd]
                self.log(f"{cmd_name} : {doc}", logtype="output")
                parser = getattr(func, "_argparser", None)
                if parser:
                    self.log(parser.format_help(), logtype="output")
                self.log("",logtype="output")
                return
            else: 

                if namespace_console:
                    # if command not found in namespace, then print help for the namespace
                    self.log(f"No help found for command '{namespace}::{cmd_name}'", logtype="output")
                    print_namespace_console._help()
                else:
                    self.log(f"No help found for command '{cmd_name}'", logtype="output")
                return
        # self.log(str(self.command_list), logtype="output")
        # TODO: with alias

        # 如果只有 union 自身的命令，可以直接打印
        if not self.namespaced_consoles:
            super()._help()
            return

        # 打印每个 console 的 help
        for ns, console in self.namespaced_consoles.items():
            self.log(f"[Namespace: {ns}] Commands:", logtype="output")
            command_doc_lst = [
                f"{cmd}\t: {console.get_cmd_doc(cmd)}"
                for cmd in console.command_dict.keys()
            ]
            if command_doc_lst:
                self.log("\n".join(command_doc_lst), logtype="output")
            else:
                self.log("  (no commands)", logtype="output")
            self.log("-" * 40, logtype="output")  # 分隔线

    def __add__(self, other: "Console") -> "UnionConsole":
        if isinstance(other, UnionConsole):
            if other.namespace == self.namespace:
                return UnionConsole(
                        list(self.namespaced_consoles.values()) 
                        + list(other.namespaced_consoles.values()), 
                        namespace=self.namespace)
            else:
                raise NotImplementedError("Merging UnionConsoles with different namespaces not implemented")
        elif isinstance(other, Console):
            return UnionConsole(list(self.namespaced_consoles.values()) + [other], namespace=self.namespace)
        else:
            raise TypeError(f"Cannot add UnionConsole with {type(other)}")
