# TODO: loggble
from typing import List, Union
import logging
from logging import Logger, Handler

GAME_LOG = 51
logging.addLevelName(GAME_LOG, "game log")

class Loggable(Logger):

    all_loggables = []
    default_handlers = []
    def __init__(self, name=None, level=logging.DEBUG):
        if not hasattr(self, "isLoggableInit"):
            if name is None: 
                if not hasattr(self, "name"):
                    name = "anon"
                else:
                    name = self.name
            Logger.__init__(self, name)
            self.setLevel(level)
            Loggable.all_loggables.append(self)
            self.addHandlers(Loggable.default_handlers)
            self.isLoggableInit = True

    def log(self, s:str, logtype=GAME_LOG):
        if logtype == "print":
            print(s)
        else:
            self.gamelog(s)

    def gamelog(self, s:str, *args):
        self._log(GAME_LOG, s, args)

    def addHandlers(self, handlers):
        for handler in handlers:
            self.addHandler(handler)

    @classmethod
    def add_handlers_for_all(cls, handlers:Union[Handler, List[Handler]], default=True):
        
        if isinstance(handlers, Handler):
            handlers = [handlers]
        if default:
            cls.default_handlers += handlers
        for loggable in cls.all_loggables:
            loggable.addHandlers(handlers)
            
