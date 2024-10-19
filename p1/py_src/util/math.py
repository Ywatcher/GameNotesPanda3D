# -*- coding: utf-8-*-

import torch
import sympy as sp
def safe_reciprocal(x):
    return torch.where(x==0, 0*x, torch.reciprocal(x))

one = sp.Number(1)
