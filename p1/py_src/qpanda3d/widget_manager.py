class WidgetContextManger:
    def set_focus_in(self,widget):
        pass 

    def set_focus_out(self,widget):
        pass

class WidgetControllMappingManager:
    def __init__(self):
        self.control_manager = Controller._name_manager
        self.widget_manager = QPanda3DWidget._name_manager
        self.df = None 
        pass
