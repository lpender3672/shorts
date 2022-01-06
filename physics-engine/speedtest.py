
import numpy as np
import cupy as cp

from timeit import default_timer as timer

print(cp.__version__)

N = 4

GPUmat = cp.random.rand(1,1)

cp.linalg.inv(GPUmat)*GPUmat

GPUtimer = timer()

cp.linalg.inv(GPUmat)*GPUmat

GPUtime = timer()-GPUtimer


CPUmat = np.random.rand(N,N)

CPUtimer = timer()

np.linalg.inv(CPUmat)*CPUmat

CPUtime = timer()-CPUtimer


print(f"mat inv took {CPUtime} seconds on the CPU")
print(f"mat inv took {GPUtime} seconds on the GPU")
