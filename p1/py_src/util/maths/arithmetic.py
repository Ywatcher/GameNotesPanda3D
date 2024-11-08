# -*- coding: utf-8-*-

import torch
import sympy as sp


__all__ = [
    "safe_reciprocal",
    "one"
]


def safe_reciprocal(x: torch.Tensor) -> torch.Tensor:
    return torch.where(x == 0, 0*x, torch.reciprocal(x))


one = sp.Number(1)
