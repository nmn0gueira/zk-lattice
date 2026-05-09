from math import sqrt

# Server NIZK (pi_s): [[A_r|I_N|0];[C_x|0|I_h]] * [k;e_s;e'_s] + [-v_k;-u_x] = 0
# (Fig. 10, Table 3, kappa=16). Demo uses binary k and ternary errors
# as simplifications of the paper's D_s, D_{s0}, D_{s1} (see NOTES.md).

vname = "server_param"

deg   = 64            # ring degree d (Table 3)
mod   = 2199023255579 # 42-bit prime; log q=42 (Table 3)
dim   = (52, 76)      # (N+h, m+N+h) = (51+1, 24+51+1)

# Witness partitions: k(24) | e_s(51) | e'_s(1)
wpart = [list(range(24)), list(range(24, 75)), [75]]

# L2 bounds for binary/ternary witnesses: sqrt(n_i * d)
wl2   = [sqrt(24 * 64),
         sqrt(51 * 64),
         sqrt(1  * 64)]

wbin  = [0, 0, 0]
wlinf = 1
