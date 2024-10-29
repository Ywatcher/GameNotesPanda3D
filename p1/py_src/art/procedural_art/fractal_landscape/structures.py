import torch
class HyperEdge:
    def __init__(self, nodes):
        self.nodes = (
            n for n in nodes
        )

    def __hash__(self):
        return self.nodes.hash()

class GeomVertex:
    coord: torch.Tensor

