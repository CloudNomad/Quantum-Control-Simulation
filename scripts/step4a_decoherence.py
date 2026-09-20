"""Step 4a: add decoherence via collapse operators (T1/T2 relaxation).

Two independent effects are modeled with Lindblad collapse operators:
  - T1 (energy relaxation): the qubit decays from |1> to |0> at rate 1/T1.
    QuTiP's sigmap() is the |1><0|-style operator that maps |1> -> |0> given
    basis(2, 0) = |0> and basis(2, 1) = |1>, so the collapse operator is
    sqrt(1/T1) * sigmap() (note: this is the opposite of what the name
    "sigmap" suggests in the usual raising/lowering convention).
  - T2 (dephasing): coherence between |0> and |1> decays, via an additional
    pure-dephasing collapse operator sqrt(gamma_phi) * sigma_z.

We first verify each effect against its expected exponential decay, then show
how decoherence degrades the pi-pulse from Step 3 when the pulse duration is
no longer negligible compared to T1/T2.
"""

import numpy as np
import qutip
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

OUTPUT_DIR = "figures"


def exp_decay(t, tau, a, c):
    return a * np.exp(-t / tau) + c


def verify_t1_decay():
    """|1> under only a sigma_minus collapse operator should decay as exp(-t/T1)."""
    T1 = 4.0
    tlist = np.linspace(0, 4 * T1, 200)
    c_ops = [np.sqrt(1 / T1) * qutip.sigmap()]
    result = qutip.mesolve(0 * qutip.qeye(2), qutip.basis(2, 1), tlist, c_ops=c_ops, e_ops=[qutip.num(2)])
    pop1 = result.expect[0]

    popt, _ = curve_fit(exp_decay, tlist, pop1, p0=[T1, 1, 0])
    fitted_T1 = popt[0]
    print(f"T1 relaxation: set T1={T1}, fitted T1={fitted_T1:.4f}")
    assert np.isclose(fitted_T1, T1, rtol=0.02), "fitted T1 should match the set T1"
    return tlist, pop1, T1


def verify_t2_dephasing():
    """|+> loses x-coherence at an effective rate set by T1 and pure dephasing."""
    T1 = 4.0
    gamma_phi = 0.6
    tlist = np.linspace(0, 4, 200)
    psi0 = (qutip.basis(2, 0) + qutip.basis(2, 1)).unit()
    c_ops = [np.sqrt(1 / T1) * qutip.sigmap(), np.sqrt(gamma_phi) * qutip.sigmaz()]
    result = qutip.mesolve(0 * qutip.qeye(2), psi0, tlist, c_ops=c_ops, e_ops=[qutip.sigmax()])
    sx = result.expect[0]

    popt, _ = curve_fit(exp_decay, tlist, sx, p0=[1.0, 1, 0])
    fitted_T2 = popt[0]
    print(f"T2 dephasing: T1={T1}, gamma_phi={gamma_phi}, fitted T2={fitted_T2:.4f}")
    assert fitted_T2 < 2 * T1, "T2 must not exceed the physical bound 2*T1"
    return tlist, sx, fitted_T2


def pi_pulse_with_decoherence(T1, T2):
    """Re-run the Step 3 pi-pulse, now with T1/T2 collapse operators active."""
    omega_rabi = 2 * np.pi * 1.0
    t_pi = np.pi / omega_rabi
    gamma_phi = max(1 / T2 - 1 / (2 * T1), 0)
    c_ops = [np.sqrt(1 / T1) * qutip.sigmap(), np.sqrt(gamma_phi) * qutip.sigmaz()]

    tlist = np.linspace(0, t_pi, 100)
    H = 0.5 * omega_rabi * qutip.sigmax()
    result = qutip.mesolve(H, qutip.basis(2, 0), tlist, c_ops=c_ops, e_ops=[qutip.sigmaz()])
    final_pop1 = (1 - result.expect[0][-1]) / 2
    return t_pi, final_pop1


def main():
    t1_tlist, pop1, T1 = verify_t1_decay()
    t2_tlist, sx, fitted_T2 = verify_t2_dephasing()

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(t1_tlist, pop1)
    axes[0].set_title(f"T1 relaxation (T1={T1})")
    axes[0].set_xlabel("time (s)")
    axes[0].set_ylabel(r"population in $|1\rangle$")

    axes[1].plot(t2_tlist, sx)
    axes[1].set_title(f"T2 dephasing (fitted T2={fitted_T2:.2f})")
    axes[1].set_xlabel("time (s)")
    axes[1].set_ylabel(r"$\langle \sigma_x \rangle$")
    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/step4a_t1_t2_decay.png", dpi=150)
    print(f"saved plot to {OUTPUT_DIR}/step4a_t1_t2_decay.png")

    # Pi-pulse fidelity vs. how long T1/T2 are relative to the pulse duration.
    t_pi_ideal = np.pi / (2 * np.pi * 1.0)
    ratios = np.array([2, 5, 10, 20, 50, 100, 200])  # T1 / t_pi
    fidelities = []
    for ratio in ratios:
        T1 = ratio * t_pi_ideal
        T2 = 1.5 * T1  # keep T2 <= 2*T1, a typical experimental ballpark
        _, final_pop1 = pi_pulse_with_decoherence(T1, T2)
        fidelities.append(final_pop1)
    fidelities = np.array(fidelities)

    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.plot(ratios, fidelities, "o-")
    ax2.set_xscale("log")
    ax2.set_xlabel(r"$T_1$ / pulse duration")
    ax2.set_ylabel(r"population in $|1\rangle$ after pi-pulse")
    ax2.set_title("Pi-pulse fidelity degrades as decoherence time approaches pulse duration")
    fig2.tight_layout()
    fig2.savefig(f"{OUTPUT_DIR}/step4a_pi_pulse_fidelity_vs_decoherence.png", dpi=150)
    print(f"saved plot to {OUTPUT_DIR}/step4a_pi_pulse_fidelity_vs_decoherence.png")

    assert fidelities[-1] > fidelities[0], "fidelity should improve as T1/T2 grow relative to pulse duration"
    print(f"fidelity at T1/t_pi={ratios[0]}: {fidelities[0]:.4f}; at T1/t_pi={ratios[-1]}: {fidelities[-1]:.4f}")


if __name__ == "__main__":
    main()
