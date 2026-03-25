from abc import ABC

import torch 


class CMG(ABC):
    @property
    def isMomentumSaturated(self) -> bool:
        """
        Check if any CMG is at its angular momentum limit
        """
        H = self.currentArrayH  # [n,3]
        H_norm = torch.linalg.norm(H, dim=1)
        H_max = self.H_max  # 每个飞轮的极限
        return torch.any(H_norm >= H_max)
