# -*- coding: utf-8-*-

from abc import ABC
import sympy as sp
class ElectricityAppliance(ABC):
    """
    This is the abstract class electricity appliances;
    this kind of object need to absorb energy in the form
    of electricity to maintain its function
    """

    def set_supply(self, supply):
        """
        set the source of electricity supply for this
        object
        params:
            supply: TODO
        """
        pass

    def get_voltage(self) -> sp.Expr:
        """
        Abstract method to obtain the current voltage across this electrical device.

        This method should be implemented by subclasses to return the symbolic
        expression representing the voltage across the two terminals of the device.
        The voltage is typically used in game simulations to model electrical behavior
        and interactions within circuits, providing real-time voltage data for different
        components.

        Returns:
            sp.Expr: A SymPy expression representing the voltage across the device.
        """

        pass

    def get_current(self) -> sp.Expr:
        pass

    @property
    def voltage(self) -> sp.Expr:
        """
        This method provides the current voltage across this electrical device/
        It calls self.get_voltage() and serves as a property
        """
        return self.get_voltage()

    @property
    def current(self) -> sp.Expr:
        """
        This method provides the current current going in and out this electrical device/
        It calls self.get_current() and serves as a property
        """
        pass
    pass
