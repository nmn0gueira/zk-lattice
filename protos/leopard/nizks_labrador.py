import sys
sys.path.insert(0, '../../lazer/python')

from lazer import polymat_t, polyvec_t, poly_t
from labrador import proof_statement, pack_verify, LAB_RING_40
from nizks import D, M, N, H, SEED_Ar, SEED_Bx, SEED_K, SEED_ES, SEED_R, SEED_EPS

# Paper uses a 42-bit prime (this is an approximation)
LAB    = LAB_RING_40
LPSIZE = "40"

# Protocol state in LAB_RING_48
A_r = polymat_t(LAB, N, M);  A_r.urandom(LAB.mod, SEED_Ar, 0)
_Bmat = polymat_t(LAB, 1, M);  _Bmat.urandom(LAB.mod, SEED_Bx, 0)
B_x = _Bmat.get_row(0)

k = polyvec_t(LAB, M);  k.brandom(1, SEED_K, 0)
e_s = polyvec_t(LAB, N);  e_s.urandom_bnd(-1, 1, SEED_ES, 0)
v_k = A_r * k + e_s

r = polyvec_t(LAB, N);  r.urandom_bnd(-1, 1, SEED_R, 0)
A_r_T = A_r.transpose()
C_x = A_r_T * r + B_x

e_ps = polyvec_t(LAB, H);  e_ps.urandom_bnd(-1, 1, SEED_EPS, 0)
C_x_mat = polymat_t(LAB, H, M)
for j in range(M):
    C_x_mat.set_elem(C_x[j], 0, j)
u_x = C_x_mat * k + e_ps


def run_client_nizk():
    """pi_c: A_r^T * r = C_x - B_x  (Figure 10)"""
    rhs = C_x - B_x
    PS = proof_statement([D], [N], [N*D], M, LPSIZE)
    PS.fresh_statement([A_r_T.get_row(0)], [r], rhs[0])
    for i in range(1, M):
        PS.fresh_statement([A_r_T.get_row(i)], [0], rhs[i])
    PS.smpl_verify()
    stmnt = PS.output_statement()
    proof = PS.pack_prove()
    pack_verify(proof[1:3], stmnt, LPSIZE)


def run_server_nizk():
    """pi_s: [[A_r|I_N|0];[C_x|0|I_h]] * [k;e_s;e'_s] = [v_k;u_x]  (Figure 10)"""
    A_s = polymat_t(LAB, N+H, M+N+H)
    one = poly_t(LAB, {0: 1})
    for i in range(N):
        for j in range(M):
            A_s.set_elem(A_r.get_elem(i, j), i, j)
        A_s.set_elem(one, i, M+i)
    for j in range(M):
        A_s.set_elem(C_x_mat.get_elem(0, j), N, j)
    A_s.set_elem(one, N, M+N)

    w = polyvec_t(LAB, M+N+H)
    for i in range(M): w[i]   = k[i]
    for i in range(N): w[M+i] = e_s[i]
    w[M+N] = e_ps[0]

    rhs = polyvec_t(LAB, N+H)
    for i in range(N): rhs[i] = v_k[i]
    rhs[N] = u_x[0]

    PS = proof_statement([D], [M+N+H], [(M+N+H)*D], N+H, LPSIZE)
    PS.fresh_statement([A_s.get_row(0)], [w], rhs[0])
    for i in range(1, N+H):
        PS.fresh_statement([A_s.get_row(i)], [0], rhs[i])
    PS.smpl_verify()
    stmnt = PS.output_statement()
    proof = PS.pack_prove()
    pack_verify(proof[1:3], stmnt, LPSIZE)


def main():
    print("=== LeoPaRd NIZKs with LaBRADOR ===")
    print(f"m={M}, N={N}, h={H}")
    print()
    print("--- Client NIZK (pi_c, Figure 10) ---")
    run_client_nizk()
    print()
    print("--- Server NIZK (pi_s, Figure 10) ---")
    run_server_nizk()


if __name__ == "__main__":
    main()
