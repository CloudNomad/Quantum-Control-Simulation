"""Step 3: drive a qubit with a resonant microwave pulse (Rabi oscillations).

Working in the frame rotating at the drive frequency, a resonant drive
reduces to a constant Hamiltonian H = (Omega/2) sigma_x, where Omega is the
Rabi frequency set by the drive amplitude. Starting from |0>, the qubit
population oscillates sinusoidally between |0> and |1>. A "pi-pulse" is the
drive duration that fully inverts the qubit.
"""

import numpy as np
import qutip
import matplotlib.pyplot as plt

OUTPUT_DIR = "figures"


def simulate_rabi(omega_rabi, tlist, psi0=None):
    """Evolve a qubit under a constant resonant drive of strength omega_rabi."""
    psi0 = psi0 if psi0 is not None else qutip.basis(2, 0)
    H = 0.5 * omega_rabi * qutip.sigmax()
    return qutip.mesolve(H, psi0, tlist, e_ops=[qutip.sigmax(), qutip.sigmay(), qutip.sigmaz()])


def main():
    omega_rabi = 2 * np.pi * 1.0  # Rabi frequency, 1 Hz
    tlist = np.linspace(0, 2, 400)  # two full Rabi periods
    result = simulate_rabi(omega_rabi, tlist)
    sx, sy, sz = result.expect

    # Population of |1> is (1 - <sz>) / 2.
    pop1 = (1 - sz) / 2

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(tlist, pop1)
    ax.set_xlabel("drive time (s)")
    ax.set_ylabel(r"population in $|1\rangle$")
    ax.set_title(f"Rabi oscillations (Omega = {omega_rabi / (2 * np.pi):.2f} Hz)")
    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/step3_rabi_oscillations.png", dpi=150)
    print(f"saved plot to {OUTPUT_DIR}/step3_rabi_oscillations.png")

    # Find and verify the pi-pulse: the drive duration for a full population
    # inversion is half a Rabi period, i.e. t_pi = pi / omega_rabi.
    t_pi = np.pi / omega_rabi
    pi_pulse_tlist = np.linspace(0, t_pi, 100)
    pi_result = simulate_rabi(omega_rabi, pi_pulse_tlist)
    final_pop1 = (1 - pi_result.expect[2][-1]) / 2
    print(f"pi-pulse duration: {t_pi:.4f} s, population in |1> after pulse: {final_pop1:.4f}")
    assert np.isclose(final_pop1, 1.0, atol=1e-3), "pi-pulse should fully invert the qubit"

    b = qutip.Bloch()
    sx_pi, sy_pi, sz_pi = pi_result.expect
    b.add_points([sx_pi, sy_pi, sz_pi], meth="l")
    b.add_states(qutip.basis(2, 0))
    b.add_states(qutip.basis(2, 1))
    b.save(f"{OUTPUT_DIR}/step3_bloch_pi_pulse.png")
    print(f"saved Bloch sphere trajectory to {OUTPUT_DIR}/step3_bloch_pi_pulse.png")


if __name__ == "__main__":
    main()
