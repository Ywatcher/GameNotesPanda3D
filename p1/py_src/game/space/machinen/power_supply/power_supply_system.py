from abc import ABC
from typing import List
from panda3d_game.game_object import *
from game.space.machinen.power_supply.power_generator import *
from game.space.machinen.power_supply.electricity_appliance import *
class PowerSupplySystem(ABC,GameObject):
    """
    This is the abstract class of power supply system,
    which should mange power generators and electricity appliances
    and control their behaviours on power production and usage ;
    the system should also include battery so that redundant power 
    can be properly restored after production;
    This doesnt need to be a closed-loop control system.
    """
    @property
    def inputs(self) -> List[PowerGen]:
        """
        This method should list all power supplies in the system
        """
        pass

    def add_input(self, powergen:PowerGen):
        """
        call this method to add a new power supply into the system
        """
        pass

    def add_output(self, output:ElectricityAppliance):
        """
        call this method to add a new power usage into the system
        """
        pass

    def update(self, task):
        """
        this is the task called when game timer updates
        edit this to control the system's behaviour
        """
        # TODO: power(out) = sum u*i
        # power in = sum p
        # delta E = (power in - power out)dt 
        return super().update(task)
    pass