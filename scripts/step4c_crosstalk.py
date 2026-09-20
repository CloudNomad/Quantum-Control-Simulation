"""Step 4c: crosstalk between control channels.

A control line meant to drive qubit A "leaks" a fraction chi of its
amplitude onto a neighboring qubit B's control line (e.g. capacitive
coupling between nearby wires). Working in the frame rotating at A's drive
frequency, the two-qubit Hamiltonian is:

    H = (Omega_A(t)/2) sigma_x^A + (Delta/2) sigma_z^B + (chi * Omega_A(t)/2) sigma_x^B

where Delta = omega_B - omega_A is the detuning between the two qubits'
transition frequencies. A's drive is exactly resonant with A (matching
Step 3), so A flips cleanly; B only sees an off-resonant "spectator" drive,
which causes a small unwanted (generalized Rabi) oscillation.
"""

import numpy as np
import qutip
import matplotlib.pyplot as plt

OUTPUT_DIR = "figures"

OMEGA_RABI = 2 * np.pi * 1.0
T_PI = np.pi / OMEGA_RABI

sx_A = qutip.tensor(qutip.sigmax(), qutip.qeye(2))
sz_A = qutip.tensor(qutip.sigmaz(), qutip.qeye(2))
sz_B = qutip.tensor(qutip.qeye(2), qutip.sigmaz())
sx_B = qutip.tensor(qutip.qeye(2), qutip.sigmax())


def simulate_crosstalk(chi, delta, tlist):
    H = 0.5 * OMEGA_RABI * sx_A + 0.5 * delta * sz_B + 0.5 * chi * OMEGA_RABI * sx_B
    psi0 = qutip.tensor(qutip.basis(2, 0), qutip.basis(2, 0))
    return qutip.mesolve(H, psi0, tlist, e_ops=[sz_A, sz_B])


def main():
    chi = 0.1  # 10% amplitude leakage onto the neighboring control line
    delta = OMEGA_RABI * 10  # qubit B detuned by 10x the Rabi frequency

    tlist = np.linspace(0, T_PI, 300)
    result = simulate_crosstalk(chi, delta, tlist)
    pop_A = (1 - result.expect[0]) / 2
    pop_B = (1 - result.expect[1]) / 2

    print(f"qubit A population in |1> at end of its pi-pulse: {pop_A[-1]:.4f}")
    print(f"qubit B (spectator) peak leaked population: {pop_B.max():.5f}")
    assert pop_A[-1] > 0.99, "crosstalk onto B should not spoil A's own pi-pulse"
    assert pop_B.max() > 0, "some leakage onto the spectator qubit is expected"

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(11, 4))
    ax_a.plot(tlist, pop_A, color="tab:blue")
    ax_a.set_xlabel("time (s)")
    ax_a.set_ylabel(r"population in $|1\rangle$")
    ax_a.set_title("Qubit A (target): clean pi-pulse")

    ax_b.plot(tlist, pop_B, color="tab:orange")
    ax_b.set_xlabel("time (s)")
    ax_b.set_ylabel(r"population in $|1\rangle$ (spectator)")
    ax_b.set_title(f"Qubit B (spectator): chi={chi}, detuning={delta / OMEGA_RABI:.0f}x Rabi freq")
    ax_b.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/step4c_crosstalk_during_pulse.png", dpi=150)
    print(f"saved plot to {OUTPUT_DIR}/step4c_crosstalk_during_pulse.png")

    # Sweep detuning: how fast does spectator leakage fall off as qubits are
    # spaced further apart in frequency?
    deltas = OMEGA_RABI * np.array([1, 2, 5, 10, 20, 50, 100, 200])
    peak_leakage = []
    for d in deltas:
        r = simulate_crosstalk(chi, d, tlist)
        peak_leakage.append(((1 - r.expect[1]) / 2).max())
    peak_leakage = np.array(peak_leakage)

    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.loglog(deltas / OMEGA_RABI, peak_leakage, "o-", label="simulated")
    # Off-resonant driving formula: leakage ~ (chi*Omega)^2 / ((chi*Omega)^2 + Delta^2)
    omega_eff = chi * OMEGA_RABI
    analytic = omega_eff**2 / (omega_eff**2 + deltas**2)
    ax2.loglog(deltas / OMEGA_RABI, analytic, "k--", label="analytic max")
    ax2.set_xlabel("detuning / Rabi frequency")
    ax2.set_ylabel("peak leaked population on spectator qubit")
    ax2.set_title(f"Crosstalk leakage falls off with qubit frequency spacing (chi={chi})")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(f"{OUTPUT_DIR}/step4c_leakage_vs_detuning.png", dpi=150)
    print(f"saved plot to {OUTPUT_DIR}/step4c_leakage_vs_detuning.png")

    assert peak_leakage[-1] < peak_leakage[0], "leakage should fall as qubits are detuned further apart"


if __name__ == "__main__":
    main()
