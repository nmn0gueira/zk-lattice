from math import sqrt, log, pi

# Server NIZK (pi_s) — Gaussian witness version (paper distributions, Def. 8).
# Same relation as server_nizk_params.py; see NOTES.md for sigma/log2o mapping.

vname = "server_gaussian_param"

deg   = 64            # ring degree d (Table 3)
mod   = 2199023255579 # 42-bit prime; log q=42 (Table 3)
dim   = (52, 76)      # (N+h, m+N+h) = (51+1, 24+51+1)

# Single partition over all 76 polys instead of three separate ones.
# With three partitions lin-codegen.sage always moves e'_s (largest wl2) to the
# BDLOP m-vector, producing Em with 1 entry while the runtime accesses Em[0..2]
# — out-of-bounds segfault. One combined partition keeps Z=1 and Em[0] the only
# access, safe regardless of codegen optimization.
wpart = [list(range(76))]

# Paper Gaussian widths (Table 3)
s  = 21.5   # chi_k = D_s
s0 = 9.90   # chi = D_{s0}
s1 = 11262  # chi_1 = D_{s1}
# Do NOT rename _d to d — lin-codegen.sage owns d=64 as a Sage Integer;
# shadowing it makes k=deg/d a float and breaks range() inside the codegen.
_d = 64

# Combined L2 bound: sqrt(||k||_2^2 + ||e_s||_2^2 + ||e'_s||_2^2)
# where ||x_i||_2 <= s_i * sqrt(n_i * d) for Gaussian D_{s_i}
_wl2_k   = s  * sqrt(24 * _d)  # ≈ 843
_wl2_es  = s0 * sqrt(51 * _d)  # ≈ 566
_wl2_eps = s1 * sqrt(1  * _d)  # ≈ 90096
wl2 = [sqrt(_wl2_k**2 + _wl2_es**2 + _wl2_eps**2)]  # ≈ 90102

wbin = [0]

# L∞ tail bound: union bound over all 76*64=4864 coefficients at delta=2^-128,
# dominated by e'_s: s1 * sqrt(ln(2*n_total*d / delta) / pi) ≈ 62871.
# Large wlinf loosens proof params vs. ternary wlinf=1; paper uses LaBRADOR.
delta = 2**-128
_n_total_d = 76 * _d
wlinf = int(s1 * sqrt(log(2 * _n_total_d / delta) / pi)) + 1  # = 62871
