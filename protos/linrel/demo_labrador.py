import sys
sys.path.insert(0, '../../lazer/python')

from lazer import polymat_t, polyvec_t
from labrados import proof_statement, pack_verify, LAB_RING_32

# LaBRADOR is hardcoded to d=64; use LAB_RING_32 (d=64, ~32-bit prime).
# Same relation as demo.py: prove knowledge of binary s s.t. A*s = t,
# A in R^(4x8). Note: demo.py uses d=256, this uses d=64.

def main():
    seed = b'\0' * 32
    m, n = 4, 8

    A = polymat_t(LAB_RING_32, m, n)
    A.urandom(LAB_RING_32.mod, seed, 0)

    s = polyvec_t(LAB_RING_32, n)
    s.brandom(1, seed, 0)

    t = A * s

    # Declare the proof: [deg], [n_witness_polys], [l2²_bound], n_constraints, primesize
    PS = proof_statement([64], [n], [n * 64], m, "32")

    # Add constraints row by row; first call registers the witness
    PS.fresh_statement([A.get_row(0)], [s], t[0])
    for i in range(1, m):
        PS.fresh_statement([A.get_row(i)], [0], t[i])  # 0 = index of s above

    PS.smpl_verify()
    stmnt = PS.output_statement()

    print("generating proof ...")
    proof_out = PS.pack_prove()

    print("verifying proof ...")
    pack_verify(proof_out[1:3], stmnt, "32")

if __name__ == "__main__":
    main()
