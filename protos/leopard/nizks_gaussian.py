import sys
import time
sys.path.insert(0, '../../lazer/python')

from lazer import (
    polyring_t, polymat_t, polyvec_t, poly_t,
    lin_prover_state_t, lin_verifier_state_t, VerificationError
)
from _client_nizk_params_cffi import lib as client_lib
from _server_nizk_gaussian_params_cffi import lib as server_lib

# LeoPaRd parameters (Table 3, kappa=16, 128-bit security)
D   = 64            # ring degree d
Q   = 2199023255579 # 42-bit prime, log q=42
M   = 24            # key dimension m = n_s
L   = 27            # client MLWE dimension ell = n_c
N   = M + L         # MLWE samples N = m + ell = 51 (paper page 29)
H   = 1             # number of output rows h

# grandom(log2o) samples D_{sigma} with sigma = 1.55 * 2^log2o (log2o must be integer).
# Mapping from paper's s (Def. 8 rho_s): sigma = s/sqrt(2*pi), log2o = round(log2(sigma/1.55)).
LOG2O_K   = 2   # k   : s=21.5  -> sigma≈8.58  -> sigma_lazer=6.20  (~28% under)
LOG2O_ES  = 1   # e_s : s0=9.90 -> sigma≈3.95  -> sigma_lazer=3.10  (~22% under)
LOG2O_EPS = 12  # e'_s: s1=11262-> sigma≈4493  -> sigma_lazer=6349  (~41% over)

SEED_Ar  = b'\x01' * 32  # mocks RO_r (Fig. 8 F.PreProcServer, derives A_r from c_r)
SEED_Bx  = b'\x02' * 32  # mocks H(x,t) (Fig. 9 F.Request line 5)
SEED_K   = b'\x03' * 32  # server key k
SEED_ES  = b'\x04' * 32  # server MLWE error e_s
SEED_R   = b'\x05' * 32  # client randomness R (chi_r = U(S_{beta_r}), beta_r=1)
SEED_EPS = b'\x06' * 32  # server eval error e'_s
SEED_PRF = b'\x00' * 32  # seed for proof randomness (same for both proofs — demo only)

Rq = polyring_t(D, Q)

def setup_protocol_state():
    """Construct LeoPaRd protocol state using paper's Gaussian distributions (Figures 8-9)."""

    # A_r ~ U(R_q^(N x m)): mocks RO_r output (Fig. 8 F.PreProcServer line 3)
    A_r = polymat_t(Rq, N, M)
    A_r.urandom(Q, SEED_Ar, 0)

    # B_x ~ U(R_q^(h x m)): mocks H(x,t) (Fig. 9 F.Request line 5)
    # polyvec_t lacks urandom; sample as 1×M matrix and extract the row.
    _B_x_mat = polymat_t(Rq, 1, M)
    _B_x_mat.urandom(Q, SEED_Bx, 0)
    B_x_row = _B_x_mat.get_row(0)

    # k ~ D_s (s=21.5, Table 3): server key (Fig. 8 F.KeyGen)
    k = polyvec_t(Rq, M)
    k.grandom(LOG2O_K, SEED_K, 0)

    # e_s ~ D_{s0} (s0=9.90, Table 3): MLWE error (Fig. 8 F.PreProcServer line 5)
    e_s = polyvec_t(Rq, N)
    e_s.grandom(LOG2O_ES, SEED_ES, 0)

    v_k = A_r * k + e_s  # Fig. 8 F.PreProcServer line 6

    # r ~ chi_r = U(S_1), ternary: client randomness (Fig. 8 F.PreProcClient line 2)
    r_row = polyvec_t(Rq, N)
    r_row.urandom_bnd(-1, 1, SEED_R, 0)

    A_r_T = A_r.transpose()
    C_x_vec = A_r_T * r_row + B_x_row  # Fig. 9 F.Request line 6

    # e'_s ~ D_{s1} (s1=11262, Table 3): eval error (Fig. 9 F.BlindEval line 8)
    e_prime_s = polyvec_t(Rq, H)
    e_prime_s.grandom(LOG2O_EPS, SEED_EPS, 0)

    C_x_mat = polymat_t(Rq, H, M)
    for j in range(M):
        C_x_mat.set_elem(C_x_vec[j], 0, j)
    u_x = C_x_mat * k + e_prime_s  # Fig. 9 F.BlindEval line 9

    return A_r, A_r_T, B_x_row, C_x_vec, C_x_mat, k, e_s, v_k, r_row, e_prime_s, u_x


def run_client_nizk(A_r_T, r_row, B_x_row, C_x_vec):
    """
    Client NIZK (pi_c): prove knowledge of r s.t. A_r^T * r + (B_x - C_x) = 0
    (Figure 10 of paper). Client witness r is ternary — same as in leopard_nizks.py.
    """
    params = client_lib.get_params("client_param")
    prover   = lin_prover_state_t(SEED_PRF, params)
    verifier = lin_verifier_state_t(SEED_PRF, params)

    A_lin = A_r_T
    t = B_x_row - C_x_vec

    prover.set_statement(A_lin, t)
    prover.set_witness(r_row)

    t0 = time.perf_counter()
    proof = prover.prove()
    t_prove = time.perf_counter() - t0

    verifier.set_statement(A_lin, t)

    t0 = time.perf_counter()
    try:
        verifier.verify(proof)
        result = "accept"
    except VerificationError:
        result = "reject"
    t_verify = time.perf_counter() - t0

    return result, len(proof), t_prove, t_verify


def run_server_nizk(A_r, C_x_mat, k, e_s, v_k, e_prime_s, u_x):
    """
    Server NIZK (pi_s): prove knowledge of (k, e_s, e'_s) such that
      A_r*k + e_s = v_k  and  C_x*k + e'_s = u_x
    Stacked as one lin proof (Figure 10 of paper):
      [[A_r | I_N | 0  ]   [k    ]   [-v_k]
       [C_x | 0   | I_h]] * [e_s  ] + [-u_x] = 0
                             [e'_s ]
    Uses server_nizk_gaussian_params: wl2 from paper's Gaussian norm bounds
    s_i * sqrt(n_i * d), wlinf from Gaussian tail bound at delta=2^-128.
    """
    params = server_lib.get_params("server_gaussian_param")
    prover   = lin_prover_state_t(SEED_PRF, params)
    verifier = lin_verifier_state_t(SEED_PRF, params)

    A_lin = polymat_t(Rq, N + H, M + N + H)  # 52 x 76
    one = poly_t(Rq, {0: 1})

    # A_r block: rows 0..N-1, cols 0..M-1
    for i in range(N):
        for j in range(M):
            A_lin.set_elem(A_r.get_elem(i, j), i, j)

    # I_N block: rows 0..N-1, cols M..M+N-1
    for i in range(N):
        A_lin.set_elem(one, i, M + i)

    # C_x block: row N, cols 0..M-1
    for j in range(M):
        A_lin.set_elem(C_x_mat.get_elem(0, j), N, j)

    # I_h block: row N, col M+N
    A_lin.set_elem(one, N, M + N)

    # Witness: [k (M) | e_s (N) | e'_s (H)]
    w = polyvec_t(Rq, M + N + H)
    for i in range(M):
        w[i] = k[i]
    for i in range(N):
        w[M + i] = e_s[i]
    w[M + N] = e_prime_s[0]

    # Target: [-v_k (N) | -u_x (H)]
    t = polyvec_t(Rq, N + H)
    for i in range(N):
        t[i] = -v_k[i]
    t[N] = -u_x[0]

    prover.set_statement(A_lin, t)
    prover.set_witness(w)

    t0 = time.perf_counter()
    proof = prover.prove()
    t_prove = time.perf_counter() - t0

    verifier.set_statement(A_lin, t)

    t0 = time.perf_counter()
    try:
        verifier.verify(proof)
        result = "accept"
    except VerificationError:
        result = "reject"
    t_verify = time.perf_counter() - t0

    return result, len(proof), t_prove, t_verify


def main():
    print("=== LeoPaRd NIZKs Demo — Gaussian witnesses ===")
    print(f"Ring: R_q with d={D}, log q=42 (Table 3, kappa=16)")
    print(f"m={M}, ell={L}, N={N}, h={H}, beta_r=1")
    print("Server witness distributions: paper's Gaussians D_s")
    print(f"  k:    log2o={LOG2O_K}  -> sigma=1.55*2^{LOG2O_K}={1.55*2**LOG2O_K:.2f}  (paper: s=21.5 -> sigma=8.58)")
    print(f"  e_s:  log2o={LOG2O_ES}  -> sigma=1.55*2^{LOG2O_ES}={1.55*2**LOG2O_ES:.2f}  (paper: s0=9.90 -> sigma=3.95)")
    print(f"  e'_s: log2o={LOG2O_EPS} -> sigma=1.55*2^{LOG2O_EPS}={1.55*2**LOG2O_EPS:.2f} (paper: s1=11262 -> sigma=4493)")
    print()

    print("Setting up fake protocol state (Figures 8 and 9)...")
    A_r, A_r_T, B_x_row, C_x_vec, C_x_mat, k, e_s, v_k, r_row, e_prime_s, u_x = \
        setup_protocol_state()
    print("Done.\n")

    print("--- Client NIZK (pi_c, Figure 10) ---")
    print("Relation: A_r^T * r + (B_x - C_x) = 0")
    result_c, size_c, t_prove_c, t_verify_c = run_client_nizk(
        A_r_T, r_row, B_x_row, C_x_vec)
    print(f"Result:   {result_c}")
    print(f"Proof size: {size_c} bytes")
    print(f"Prove:    {t_prove_c:.3f} s")
    print(f"Verify:   {t_verify_c:.3f} s")
    print()

    print("--- Server NIZK (pi_s, Figure 10) ---")
    print("Relation: [[A_r|I_N|0];[C_x|0|I_h]] * [k;e_s;e'_s] + [-v_k;-u_x] = 0")
    result_s, size_s, t_prove_s, t_verify_s = run_server_nizk(
        A_r, C_x_mat, k, e_s, v_k, e_prime_s, u_x)
    print(f"Result:   {result_s}")
    print(f"Proof size: {size_s} bytes")
    print(f"Prove:    {t_prove_s:.3f} s")
    print(f"Verify:   {t_verify_s:.3f} s")


if __name__ == "__main__":
    main()
