"""Step 4b: pulse amplitude and timing jitter.

Real pulse generators and amplifiers do not deliver exactly the same pulse
every shot: the amplitude fluctuates from shot to shot (e.g. amplifier
noise), and the effective drive duration is imprecise (e.g. clock/trigger
jitter). We model both as per-shot Gaussian noise on top of the ideal
pi-pulse calibrated in Step 3, run a Monte Carlo over many shots, and
measure how the pulse infidelity scales with jitter magnitude.
"""

import numpy as np
import qutip
import matplotlib.pyplot as plt

OUTPUT_DIR = "figures"
RNG = np.random.default_rng(42)

OMEGA_RABI = 2 * np.pi * 1.0
T_PI_IDEAL = np.pi / OMEGA_RABI


def run_shot(amp_jitter_std, time_jitter_std):
    """Run one pi-pulse shot with Gaussian amplitude/timing jitter, return infidelity."""
    omega = OMEGA_RABI * (1 + RNG.normal(0, amp_jitter_std))
    duration = T_PI_IDEAL * (1 + RNG.normal(0, time_jitter_std))
    H = 0.5 * omega * qutip.sigmax()
    result = qutip.mesolve(H, qutip.basis(2, 0), [0, duration], e_ops=[qutip.sigmaz()])
    pop1 = (1 - result.expect[0][-1]) / 2
    return 1 - pop1  # infidelity: how far short of full inversion


def sweep_jitter(jitter_stds, n_shots, mode):
    """Average infidelity over n_shots Monte Carlo shots for each jitter level."""
    mean_infidelity = np.zeros(len(jitter_stds))
    std_infidelity = np.zeros(len(jitter_stds))
    for i, jitter in enumerate(jitter_stds):
        amp_std = jitter if mode == "amplitude" else 0.0
        time_std = jitter if mode == "timing" else 0.0
        shots = np.array([run_shot(amp_std, time_std) for _ in range(n_shots)])
        mean_infidelity[i] = shots.mean()
        std_infidelity[i] = shots.std()
    return mean_infidelity, std_infidelity


def main():
    n_shots = 300
    jitter_stds = np.array([0.0, 0.01, 0.02, 0.05, 0.1, 0.2])

    amp_mean, amp_std = sweep_jitter(jitter_stds, n_shots, "amplitude")
    time_mean, time_std = sweep_jitter(jitter_stds, n_shots, "timing")

    print("amplitude jitter std -> mean infidelity:")
    for j, m in zip(jitter_stds, amp_mean):
        print(f"  {j:.2f} -> {m:.5f}")
    print("timing jitter std -> mean infidelity:")
    for j, m in zip(jitter_stds, time_mean):
        print(f"  {j:.2f} -> {m:.5f}")

    assert amp_mean[-1] > amp_mean[0], "infidelity should grow with amplitude jitter"
    assert time_mean[-1] > time_mean[0], "infidelity should grow with timing jitter"

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.errorbar(jitter_stds * 100, amp_mean, yerr=amp_std, marker="o", label="amplitude jitter")
    ax.errorbar(jitter_stds * 100, time_mean, yerr=time_std, marker="s", label="timing jitter")
    ax.set_xlabel("jitter std (% of nominal)")
    ax.set_ylabel("mean pi-pulse infidelity")
    ax.set_title(f"Pi-pulse infidelity vs. control jitter ({n_shots} shots/point)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/step4b_jitter_infidelity.png", dpi=150)
    print(f"saved plot to {OUTPUT_DIR}/step4b_jitter_infidelity.png")

    # Single-shot distribution at a realistic jitter level, to show the spread
    # a calibration routine has to contend with (not just the mean).
    jitter = 0.05
    shots = np.array([run_shot(jitter, jitter) for _ in range(1000)])
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.hist(shots, bins=40)
    ax2.set_xlabel("pi-pulse infidelity")
    ax2.set_ylabel("shots")
    ax2.set_title(f"Infidelity distribution, {jitter * 100:.0f}% amplitude+timing jitter, 1000 shots")
    fig2.tight_layout()
    fig2.savefig(f"{OUTPUT_DIR}/step4b_jitter_distribution.png", dpi=150)
    print(f"saved plot to {OUTPUT_DIR}/step4b_jitter_distribution.png")


if __name__ == "__main__":
    main()
