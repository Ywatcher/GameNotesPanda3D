from ui.abstract_ui import AbstractGUI
class QtGUI(AbstractGUI):
    def __init__(self) -> None:
        super().__init__()


        self.outFocusKeyPressEnabled = 0
        # TODO: what does it do
        self.keyPressEnabled = 1 # TODO: set it
        # use command or hotkey

    # TODO: use command to set it
    def setOutFocusKeyPress(self, enable:bool=True):
        self.outFocusKeyPressEnabled = enable


class RawQtGUI(QtGUI):
    # triggers _manager_start_game when starts
    pass

class AdvancedQtGUI(QtGUI):
    # create a menu, with buttons to start game
    # button "new window"
    pass

