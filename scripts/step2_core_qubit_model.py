"""Step 2: represent a qubit as a two-level system and simulate free evolution.

A qubit initialized on the equator of the Bloch sphere, evolving under a
static sigma_z Hamiltonian, should precess around the z-axis at the qubit's
transition frequency (Larmor precession). We confirm that behavior here.
"""

import numpy as np
import qutip
import matplotlib.pyplot as plt

OUTPUT_DIR = "figures"


def main():
    omega = 2 * np.pi * 1.0  # qubit frequency, 1 Hz for readability
    H = 0.5 * omega * qutip.sigmaz()

    # Start on the equator (|+>) so precession is visible in <sx>, <sy>.
    psi0 = (qutip.basis(2, 0) + qutip.basis(2, 1)).unit()

    tlist = np.linspace(0, 2, 400)  # two full periods
    e_ops = [qutip.sigmax(), qutip.sigmay(), qutip.sigmaz()]
    result = qutip.mesolve(H, psi0, tlist, e_ops=e_ops)
    sx, sy, sz = result.expect

    period = 2 * np.pi / omega
    print(f"qubit frequency: {omega / (2 * np.pi):.3f} Hz, period: {period:.3f} s")
    print(f"<sz> range: [{sz.min():.4f}, {sz.max():.4f}] (expect ~0, no z-dynamics)")
    assert np.allclose(sz, 0, atol=1e-6), "sigma_z Hamiltonian should not change <sz>"

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(tlist, sx, label=r"$\langle \sigma_x \rangle$")
    ax.plot(tlist, sy, label=r"$\langle \sigma_y \rangle$")
    ax.plot(tlist, sz, label=r"$\langle \sigma_z \rangle$")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("expectation value")
    ax.set_title("Free evolution of a qubit (Larmor precession)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/step2_free_evolution.png", dpi=150)
    print(f"saved plot to {OUTPUT_DIR}/step2_free_evolution.png")

    b = qutip.Bloch()
    b.add_points([sx, sy, sz], meth="l")
    b.save(f"{OUTPUT_DIR}/step2_bloch_precession.png")
    print(f"saved Bloch sphere trajectory to {OUTPUT_DIR}/step2_bloch_precession.png")


if __name__ == "__main__":
    main()
