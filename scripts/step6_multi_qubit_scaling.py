"""Step 6: extend to a small multi-qubit register and explore scaling.

Generalizes the Step 4c crosstalk model (one target qubit driven resonantly,
one detuned spectator picking up leaked drive from the same control line) to
a register of 2-3 qubits built as an explicit multi-qubit tensor-product
Hilbert space, then further to a broader register-size sweep to see how the
crosstalk error budget scales as more qubits share control infrastructure.

Because none of the Hamiltonian terms couple different qubits to each other
(crosstalk here is classical leakage between control lines, not a physical
qubit-qubit interaction), the full-register Hamiltonian is an uncoupled sum
H = H_0 + H_1 + ... + H_{N-1} acting on separate tensor factors. Starting
from a product state, the exact evolution stays a product state for all
time. We first verify this explicitly for a real 2- and 3-qubit tensor-
product simulation (the concrete case the roadmap asks for), then use the
much cheaper equivalent independent single-qubit calculation to explore how
the total crosstalk error scales as the register grows well past 3 qubits.
"""

import numpy as np
import qutip
import matplotlib.pyplot as plt

OUTPUT_DIR = "figures"

OMEGA_RABI = 2 * np.pi * 1.0
T_PI = np.pi / OMEGA_RABI
CHI = 0.1


def build_register_operators(n_qubits):
    """sigma_x and sigma_z acting on qubit i within an n_qubits tensor product."""
    sx, sz = [], []
    for i in range(n_qubits):
        ops_x = [qutip.qeye(2)] * n_qubits
        ops_x[i] = qutip.sigmax()
        sx.append(qutip.tensor(ops_x))
        ops_z = [qutip.qeye(2)] * n_qubits
        ops_z[i] = qutip.sigmaz()
        sz.append(qutip.tensor(ops_z))
    return sx, sz


def simulate_register_tensor(detunings, chi, tlist):
    """Full tensor-product simulation: qubit 0 is the resonantly-driven
    target; qubits 1..N-1 are spectators at the given detunings, all
    picking up a leaked chi-fraction of qubit 0's drive (shared line)."""
    n_qubits = len(detunings) + 1
    sx, sz = build_register_operators(n_qubits)

    H = 0.5 * OMEGA_RABI * sx[0]
    for i, delta in enumerate(detunings, start=1):
        H = H + 0.5 * delta * sz[i] + 0.5 * chi * OMEGA_RABI * sx[i]

    psi0 = qutip.tensor([qutip.basis(2, 0)] * n_qubits)
    return qutip.mesolve(H, psi0, tlist, e_ops=sz)


def spectator_leakage_independent(delta, chi, tlist):
    """The equivalent single-spectator problem (2-dim), used once the
    product-state factorization above has been verified, to explore larger
    registers cheaply."""
    H = 0.5 * delta * qutip.sigmaz() + 0.5 * chi * OMEGA_RABI * qutip.sigmax()
    result = qutip.mesolve(H, qutip.basis(2, 0), tlist, e_ops=[qutip.sigmaz()])
    return (1 - result.expect[0]) / 2


def target_fidelity_independent(tlist):
    H = 0.5 * OMEGA_RABI * qutip.sigmax()
    result = qutip.mesolve(H, qutip.basis(2, 0), tlist, e_ops=[qutip.sigmaz()])
    return (1 - result.expect[0]) / 2


def main():
    tlist = np.linspace(0, T_PI, 300)
    fixed_delta = OMEGA_RABI * 10

    # --- Concrete 2- and 3-qubit tensor-product simulations, as asked for ---
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, n_spectators in zip(axes, [1, 2]):
        detunings = [fixed_delta] * n_spectators
        result = simulate_register_tensor(detunings, CHI, tlist)
        pops = [(1 - e) / 2 for e in result.expect]
        ax.plot(tlist, pops[0], label="qubit 0 (target)", linewidth=2)
        for i, p in enumerate(pops[1:], start=1):
            ax.plot(tlist, p, label=f"qubit {i} (spectator)", alpha=0.8)
        ax.set_xlabel("time (s)")
        ax.set_title(f"{n_spectators + 1}-qubit register")
        ax.legend(fontsize=8)
    axes[0].set_ylabel(r"population in $|1\rangle$")
    fig.suptitle("Multi-qubit tensor-product simulation: target + spectators on a shared line")
    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/step6_2_3_qubit_registers.png", dpi=150)
    print(f"saved plot to {OUTPUT_DIR}/step6_2_3_qubit_registers.png")

    # --- Verify the product-state factorization against the cheap independent
    # calculation, before relying on it for the larger register sweep. ---
    detunings_3q = [fixed_delta, fixed_delta * 2]
    result_3q = simulate_register_tensor(detunings_3q, CHI, tlist)
    tensor_pops = [(1 - e) / 2 for e in result_3q.expect]
    independent_target = target_fidelity_independent(tlist)
    independent_spectators = [spectator_leakage_independent(d, CHI, tlist) for d in detunings_3q]

    max_diff_target = np.max(np.abs(tensor_pops[0] - independent_target))
    max_diff_spectators = max(
        np.max(np.abs(tp - ip)) for tp, ip in zip(tensor_pops[1:], independent_spectators)
    )
    print(f"max diff, tensor vs. independent (target): {max_diff_target:.2e}")
    print(f"max diff, tensor vs. independent (spectators): {max_diff_spectators:.2e}")
    # Threshold set by mesolve's default ODE solver tolerance, not physics --
    # the factorization itself is exact (H has no cross-qubit terms).
    assert max_diff_target < 1e-4, "product-state factorization should be exact for target"
    assert max_diff_spectators < 1e-4, "product-state factorization should be exact for spectators"

    # --- Scaling sweep: how does total register crosstalk error grow with N? ---
    n_spectators_range = [1, 2, 3, 4, 5, 6, 8, 10]
    total_leakage_fixed, total_leakage_fanned = [], []
    for n_spec in n_spectators_range:
        fixed_detunings = [fixed_delta] * n_spec
        fanned_detunings = [fixed_delta * (i + 1) for i in range(n_spec)]

        fixed_peaks = [spectator_leakage_independent(d, CHI, tlist).max() for d in fixed_detunings]
        fanned_peaks = [spectator_leakage_independent(d, CHI, tlist).max() for d in fanned_detunings]

        total_leakage_fixed.append(sum(fixed_peaks))
        total_leakage_fanned.append(sum(fanned_peaks))
        print(
            f"n_spectators={n_spec:2d}: total leakage fixed-spacing={sum(fixed_peaks):.5f}, "
            f"fanned-out={sum(fanned_peaks):.5f}"
        )

    total_leakage_fixed = np.array(total_leakage_fixed)
    total_leakage_fanned = np.array(total_leakage_fanned)
    assert total_leakage_fixed[-1] > total_leakage_fixed[0], "error budget should grow as more qubits share a line"
    assert total_leakage_fanned[-1] < total_leakage_fixed[-1], (
        "spreading qubits over more spectrum should curb the error growth vs. fixed spacing"
    )

    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.plot(n_spectators_range, total_leakage_fixed, "o-", label="fixed spacing (shared bus, limited spectrum)")
    ax2.plot(n_spectators_range, total_leakage_fanned, "s-", label="fanned-out spacing (spread over more spectrum)")
    ax2.set_xlabel("number of spectator qubits sharing the control line")
    ax2.set_ylabel("total crosstalk leakage across register")
    ax2.set_title("Crosstalk error budget vs. register size")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(f"{OUTPUT_DIR}/step6_scaling_leakage.png", dpi=150)
    print(f"saved plot to {OUTPUT_DIR}/step6_scaling_leakage.png")


if __name__ == "__main__":
    main()
