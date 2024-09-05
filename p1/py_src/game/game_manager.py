from p1.py_src.ui.abstract_ui import AbstractGUI


class GameManager:
    def __init__(self) -> None:
        # TODO: create a gui
        pass


    def setGUI(self, gui: AbstractGUI):
        self.gui = gui
        self.gui._manager_start_game = self.start_game
        self.gui._manager_end_game = self.end_game

    def start_game(self):
        # do not operate gui here
        pass

    def end_game(self):
        pass
