from math import sqrt

# Client NIZK (pi_c): A_r^T * r + (B_x - C_x) = 0  (Fig. 10, Table 3, kappa=16)
# r is the single row of R, treated as a column vector of N=51 polys.

vname = "client_param"

deg   = 64            # ring degree d (Table 3)
mod   = 2199023255579 # 42-bit prime; log q=42 (Table 3)
dim   = (24, 51)      # A_r^T is m x N = 24 x 51

# r ~ chi_r = U(S_1): ternary, beta_r=1 (Table 3)
wpart = [list(range(51))]
wl2   = [sqrt(51 * 64)]  # sqrt(N*d): L2 bound for ternary witness
wbin  = [0]
wlinf = 1
