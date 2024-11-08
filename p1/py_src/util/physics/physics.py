# -*- coding: utf-8-*-

import sympy as sp

from sympy.physics.units import (
    centimeter, meter, kilometer,
    gram, kilogram, tonne,
    newton,
    second
)
from typing import Union

__all__ = [
    "autocomplete_units",
    "getG",
    "G_val",

]


def autocomplete_units(unit: dict):
    """
    complete default unit settings to
    ensure dimensionless quantity is correct
    """
    force_unit = (
        unit["mass"] * unit["length"] / unit["time"] ** 2
    )/(kilogram * meter / second**2).simplify()
    unit["force"] = force_unit * newton


# default G value for gravity constant
G_val = 6.67430 * 1e-11 * newton * meter**2 / (kilogram**2)


# get float G value, given G value in symbol and unit settings
def getG(unit, G_val=G_val) -> Union[sp.Float, float]:
    G = sp.symbols('G')
    m1, m2 = sp.symbols('m1 m2')
    r = sp.symbols('r')
    M1 = m1 * unit["mass"]
    M2 = m2 * unit["mass"]
    R = r * unit["length"]
    F = G*(M1*M2)/R**2
    f = F/unit["force"]
    G_game = f.simplify().subs({
        m1: 1,
        m2: 1,
        r: 1,
        G: G_val
    })
    return G_game
