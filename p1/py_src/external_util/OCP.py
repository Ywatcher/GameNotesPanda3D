

def trsf_to_numpy(trsf):
    import numpy as np 
    mat = np.eye(4)
    for i in range(3):
        for j in range(4):
            mat[i, j] = trsf.Value(i+1, j+1)  # OCCT是1-based
    return mat

def trsf_to_numpy_fast(trsf):
    import numpy as np  
    mat = [
        [trsf.Value(i, j) for j in range(1, 5)]
        for i in range(1, 4)
    ]
    mat.append([0,0,0,1])
    return np.array(mat)



def trsf_to_torch(trsf, dtype=torch.float32):
    import torch
    mat = torch.eye(4, dtype=dtype)
    for i in range(3):
        for j in range(4):
            mat[i, j] = trsf.Value(i+1, j+1)
    return mat

