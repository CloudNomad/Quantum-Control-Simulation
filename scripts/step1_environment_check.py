"""Step 1: verify the environment can run QuTiP simulations."""

import numpy
import scipy
import matplotlib
import qutip


def main():
    print(f"qutip      {qutip.__version__}")
    print(f"numpy      {numpy.__version__}")
    print(f"scipy      {scipy.__version__}")
    print(f"matplotlib {matplotlib.__version__}")

    # Minimal sanity check: a qubit starting in |0> under a sigma_x
    # Hamiltonian should fully invert to |1> after a pi rotation.
    psi0 = qutip.basis(2, 0)
    H = (numpy.pi / 2) * qutip.sigmax()  # rotation angle = pi at t=1
    tlist = numpy.linspace(0, 1, 200)
    result = qutip.mesolve(H, psi0, tlist, e_ops=[qutip.sigmaz()])

    final_sz = result.expect[0][-1]
    assert numpy.isclose(final_sz, -1, atol=1e-3), f"expected <sz>=-1, got {final_sz}"
    print(f"sanity check passed: <sigma_z> after pi-rotation = {final_sz:.4f}")


if __name__ == "__main__":
    main()
