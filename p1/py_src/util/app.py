# import datetime
from datetime import datetime
from direct.showbase.ShowBase import ShowBase


class ContextShowBase(ShowBase):
    
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
        
    def log(self, s:str):
        print(s)
        