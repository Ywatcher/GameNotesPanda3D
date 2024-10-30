# -*- coding: utf-8-*-

# import torch


# class HyperEdge:
# def __init__(self, nodes):
# self.nodes = (
# n for n in nodes
# )

# def __hash__(self):
# return self.nodes.hash()


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
