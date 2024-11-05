# -*- coding: utf-8-*-

# import torch
from typing import List


__all__ = [
    "VertInfo", "HyperEdge"
]


class VertInfo:
    tup: tuple

    def __hash__(self):
        # unique identifier
        return self.tup.__hash__()

    def __iter__(self):
        return iter(self.tup)

    def __len__(self):
        return len(self.tup)

    def __eq__(self, other):
        return self.tup == tuple(other)

    def __ge__(self, other):
        return self.tup >= tuple(other)

    def __gt__(self, other):
        return self.tup > tuple(other)


class HyperEdge:
    @staticmethod
    def sortfn(nodes: VertInfo) -> List[VertInfo]:
        return sorted(nodes, key=lambda arg: hash(arg))

    def __init__(self, nodes):
        self._sorted = self.sortfn(nodes)

    def __len__(self):
        return len(self._sorted)

    def __hash__(self):
        return hash(self._sorted)

    def __iter__(self):
        return iter(self._sorted)
