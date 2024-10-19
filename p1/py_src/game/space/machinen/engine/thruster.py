from abc import *
import sympy as sp
import torch
from panda3d_game.game_object import *





class Thruster(ABC,PhysicsGameObject):
    @property
    def thrust_val(self) -> sp.Expr:
        pass

    @property
    def thrust_dire(self) -> torch.Tensor:
        # thrust direction
        # fixed for non vector thrust
        # return torch.Tensor(self.direction)
        pass

    @property
    def thrust(self) -> torch.Tensor:
        pass

    pass
