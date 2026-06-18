import sys
import time
sys.path.insert(0, '../../lazer/python')

from lazer import (
    polyring_t, polymat_t, polyvec_t,
    lin_prover_state_t, lin_verifier_state_t, VerificationError
)
from _params_cffi import lib


D = 64
Q = 2199023255579
M = 24 # output polynomials
M_H = 51 # input polynomials

SEED_A = b'\x07' * 32
SEED_X = b'\x08' * 32
SEED_PRF = b'\x00' * 32

Rq = polyring_t(D, Q)


def main():
    print("=== Ajtai Hash NIZK ===")
    print(f"Ring: R_q with d={D}, log_q=42")
    print(f"Hash: A in R_q^({M}x{M_H}), input x in {{-1,0,1}}^({M_H * D} coeffs), output B_x in R_q^{M}")
    print()

    A = polymat_t(Rq, M, M_H)
    A.urandom(Q, SEED_A, 0)

    x = polyvec_t(Rq, M_H)
    x.urandom_bnd(-1, 1, SEED_X, 0)

    c_vec = A * x

    params = lib.get_params("param")
    prover = lin_prover_state_t(SEED_PRF, params)
    verifier = lin_verifier_state_t(SEED_PRF, params)

    t = -c_vec

    prover.set_statement(A, t)
    prover.set_witness(x)

    t0 = time.perf_counter()
    proof = prover.prove()
    t_prove = time.perf_counter() - t0

    verifier.set_statement(A, t)

    t0 = time.perf_counter()
    try:
        verifier.verify(proof)
        result = "accept"
    except VerificationError:
        result = "reject"
    t_verify = time.perf_counter() - t0

    print(f"Proof size: {len(proof)} bytes")
    print(f"Prove:      {t_prove:.3f} s")
    print(f"Verify:     {t_verify:.3f} s")
    print(f"Result:     {result}")

if __name__ == "__main__":
    main()
