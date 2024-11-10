# -*- coding: utf-8-*-

# TODO: loggble
import sys
import os
import io
from typing import List, Union
from contextlib import contextmanager
import logging
from logging import Logger, Handler


@contextmanager
def redirect_output(
        device: Union[io.TextIOWrapper, str, os.PathLike] = os.devnull):
    """
    usage:
    with redirect_output(device):
        functionPrintSomething() # prints will be redirected
        pass
    """
    # Use provided device or default to os.devnull
    # if device is None:
    #     device = open(os.devnull, 'w')
    #     should_close = True  # Flag to close os.devnull after use
    if isinstance(device, (os.PathLike, str)):
        device = open(device, 'w', encoding='utf-8')
        should_close = True
    else:
        should_close = False  # Only close if we opened os.devnull

    # Save the current stdout
    old_stdout = sys.stdout
    sys.stdout = device
    try:
        yield  # Run code within 'with' block
    finally:
        sys.stdout = old_stdout
        if should_close:
            device.close()


GAME_LOG = 51
logging.addLevelName(GAME_LOG, "game log")


class Loggable:
    # TODO: add devices for log

    all_loggables: List['Loggable'] = []
    default_handlers: List[Handler] = []

    def __init__(self, name=None, level=logging.DEBUG, use_parent=False):
        if not hasattr(self, "isLoggableInit"):
            if name is None:
                if not hasattr(self, "name"):
                    name = "anon"
                else:
                    name = self.name
            self.logger = Logger(name)
            self.logger.setLevel(level)
            Loggable.all_loggables.append(self)
            self.addHandlers(Loggable.default_handlers)
            self.use_parent = use_parent  # TODO
            self.isLoggableInit = True

    def debug(self, *args, **kwargs):
        # self.logger.debug(*args, **kwargs)
        # FIXME
        pass

    def addHandler(self, *args, **kwargs):
        self.logger.addHandler(*args, **kwargs)

    def _log(self, *args, **kwargs):
        self.logger._log(*args, **kwargs)

    def log(self, s: str, logtype=GAME_LOG):
        if logtype == "print":
            print(s)
        else:
            self.gamelog(s)

    def gamelog(self, s: str, *args):
        self._log(GAME_LOG, s, args)

    def addHandlers(self, handlers):
        for handler in handlers:
            self.addHandler(handler)

    @classmethod
    def add_handlers_for_all(
            cls, handlers: Union[Handler, List[Handler]],
            default=True):

        if isinstance(handlers, Handler):
            handlers = [handlers]
        if default:
            cls.default_handlers += handlers
        for loggable in cls.all_loggables:
            loggable.addHandlers(handlers)

    class LogDevice(io.BufferedIOBase):
        def __init__(self, parentLoggable: "Loggable", logtype):
            pass  # TODO

    def getDevice(self, logtype):
        # TODO: more args, see help(BufferedIOBase)
        return io.TextIOWrapper(Loggable.LogDevice(self, Loggable))  # FIXME
