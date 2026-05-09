from math import sqrt

# Prove knowledge of binary s in Rp^8 such that A*s + t = 0
# A in Rp^(4x8), Rp = Zp[X]/(X^d + 1)

vname = "param"

deg  = 256
mod  = 2**32 - 4607
dim  = (4, 8)

wpart = [list(range(8))]
wl2   = [sqrt(2048)]
wbin  = [0]
wlinf = 1
