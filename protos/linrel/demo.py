import sys
sys.path.insert(0, '../../lazer/python')

from lazer import *
from _params_cffi import lib

def main():
    from params import mod, deg, dim
    d, p, m, n = deg, mod, dim[0], dim[1]

    seed   = b'\0' * 32
    params = lib.get_params("param")

    prover   = lin_prover_state_t(seed, params)
    verifier = lin_verifier_state_t(seed, params)

    Rp = polyring_t(d, p)
    A  = polymat_t(Rp, m, n)
    A.urandom(p, seed, 0)

    s = polyvec_t(Rp, n)
    s.brandom(1, seed, 0)

    t = -A * s

    prover.set_statement(A, t)
    prover.set_witness(s)

    print("generating proof ...")
    proof = prover.prove()
    print_stopwatch_lnp_prover_prove(0)

    verifier.set_statement(A, t)

    print("verifying proof ...")
    try:
        verifier.verify(proof)
    except VerificationError:
        print("reject")
    else:
        print("accept")
    print_stopwatch_lnp_verifier_verify(0)

if __name__ == "__main__":
    main()
