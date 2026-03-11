from abc import ABC 
import torch


class CMGArray(ABC): 
    """
    Array of Control Moment Gyroscopes
    """

    def __len__(self):
        # number of CMGs 
        # control algorithm can be hooked
        raise NotImplementedError

    @property
    def currentArrayH(self) -> torch.Tensor:
        """
        Current angular momentum of all CMGs
        shape: [n, 3], n = number of CMGs
        """
        raise NotImplementedError
        

    
    @property 
    def currentGimbalDirections(self) -> torch.Tensor:
        """
        Unit vectors of gimbal axes
        shape: [n, 3]
        """
        raise NotImplementedError


    @property
    def currentJacobian(self) -> torch.Tensor:
        """
        Compute CMG Jacobian matrix A, shape [3, n]
        A[:, i] = u_i x H_i
        """
        H = self.currentArrayH         # [n, 3]
        u = self.currentGimbalDirections  # [n, 3]

        # Compute cross product for each CMG: u_i x H_i
        # Result: [n,3]
        cross = torch.cross(u, H, dim=1)

        # Transpose to shape [3, n]
        A = cross.T  # [3, n]
        return A


    def isSingular(self, threshold=1e-3) -> bool:
        """
        Check if CMG array is near singularity
        threshold: minimum singular value considered non-singular
        """
        A = self.currentJacobian  # [3, n]

        # Compute singular values
        # Use torch.linalg.svdvals for PyTorch >=1.9
        sigma = torch.linalg.svdvals(A)  # returns [min(3,n)]

        # Smallest singular value
        sigma_min = sigma[-1]

        return sigma_min < threshold

