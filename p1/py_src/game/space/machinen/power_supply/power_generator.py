from abc import ABC
import sympy as sp
class PowerGen(ABC):
    """
    This is the abstract class of power generator;
    this kind of object can generate energy 
    """
    def power(self) -> sp.Expr:
        pass
    pass