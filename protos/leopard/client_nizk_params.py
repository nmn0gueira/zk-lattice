from math import sqrt

# Combined client NIZK (pi_c + pi_hash, Fig. 10, Table 3, kappa=16):
#   [A_r^T | A_H] * [r; x] + (-C_x) = 0
# Witness [r (N=51) | x (M_H=51)] stacked as one ternary partition.

vname = "client_param"

deg   = 64            # ring degree d (Table 3)
mod   = 2199023255579 # 42-bit prime; log q=42 (Table 3)
dim   = (24, 102)     # M rows, N+M_H cols

wpart = [list(range(102))]
wl2   = [sqrt(102 * 64)]
wbin  = [0]
wlinf = 1
