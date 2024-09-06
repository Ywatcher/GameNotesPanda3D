from py_src.ui.abstract_ui import AbstractGUI
from py_src.ui.gui_factory import GUIFactory

class GameManager:
    def __init__(self) -> None:
        # TODO: create a gui
        self.is_game_running = False
        pass


    def setGUI(self, gui: AbstractGUI):
        self.gui = gui
        self.gui._manager_start_game = self.start_game
        self.gui._manager_end_game = self.end_game

    def start_game(self):
        # do not operate gui here
        # if not game running
        pass

    def end_game(self):
        pass

    def run(self):
        # TODO: multithread
        pass
