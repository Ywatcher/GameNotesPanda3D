# import datetime
from datetime import datetime
from direct.showbase.ShowBase import ShowBase
from util.log import Loggable


class ContextShowBase(ShowBase, Loggable):
    # use context management to ensure the app
    # terminates correctly
    
    # @classmethod
    def remove_all_task(self):
        pass
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.remove_all_task()
        self.log(
            "---{} destroy at {}---".format(
                self, datetime.now()
            )
        )
        self.destroy()
        self.log(
            "---{} destroyed at {}, exit---".format(
                self, datetime.now()
            )
        )
        
    def run(self):
        self.log(
            "---{} run(), at {}---".format(
                self, datetime.now()
            )
        )
        super().run()
        
    def log(self, s:str):
        print(s)
        
    def __repr__(self):
        if hasattr(self, "name"):
            return self.name
        else:
            return super().__repr__()
        
        
class ControlShowBase(ContextShowBase):
    pass