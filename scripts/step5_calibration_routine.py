"""Step 5: an automated calibration routine for the pi-pulse.

On real hardware you never know the exact Rabi frequency a given drive
amplitude produces -- amplifier gain, cable loss, and mixer calibration all
drift. This script treats the qubit as a black box with an unknown true
Rabi frequency, and calibrates against it the way a real experiment would:
sweep the drive duration, measure (noisy, finite-shot) population in |1>,
fit a decaying-sinusoid Rabi model, and extract the pi-pulse duration from
the fit. We then measure how calibration accuracy depends on two realistic
noise sources: finite measurement shots and decoherence (T1/T2).
"""

import numpy as np
import qutip
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

OUTPUT_DIR = "figures"
RNG = np.random.default_rng(7)

# The device's true Rabi frequency is not exactly the nominal design value --
# e.g. amplifier gain is 7% higher than assumed. Calibration must discover this.
OMEGA_NOMINAL = 2 * np.pi * 1.0
OMEGA_TRUE = OMEGA_NOMINAL * 1.07


def true_population(omega, t, T1, T2):
    """Exact population in |1> after driving for time t at Rabi frequency omega."""
    gamma_phi = max(1 / T2 - 1 / (2 * T1), 0) if np.isfinite(T2) else 0
    c_ops = [np.sqrt(1 / T1) * qutip.sigmap()] if np.isfinite(T1) else []
    if gamma_phi > 0:
        c_ops.append(np.sqrt(gamma_phi) * qutip.sigmaz())
    H = 0.5 * omega * qutip.sigmax()
    result = qutip.mesolve(H, qutip.basis(2, 0), [0, t], c_ops=c_ops, e_ops=[qutip.sigmaz()])
    return (1 - result.expect[0][-1]) / 2


def noisy_measurement(omega, t, T1, T2, n_shots):
    """Simulate a finite-shot experiment: binomial sampling around the true population."""
    p = true_population(omega, t, T1, T2)
    if n_shots is None:
        return p
    return RNG.binomial(n_shots, p) / n_shots


def rabi_model(t, omega, t2_env, offset, amp):
    return offset + amp * np.exp(-t / t2_env) * (1 - np.cos(omega * t)) / 2


def calibrate_pi_pulse(T1, T2, n_shots, n_points=60, t_max=3 * 2 * np.pi / OMEGA_NOMINAL):
    """Sweep drive duration, fit a Rabi curve, and return the calibrated pi-pulse duration.

    The sweep spans several full Rabi periods (not just one) because fitting
    the oscillation frequency accurately -- which is what pins down the
    pi-pulse duration -- needs enough accumulated phase to average out
    shot noise; a sweep that barely covers one period is underdetermined.
    """
    tlist = np.linspace(0, t_max, n_points)
    pops = np.array([noisy_measurement(OMEGA_TRUE, t, T1, T2, n_shots) for t in tlist])

    p0 = [OMEGA_NOMINAL, T2 if np.isfinite(T2) else 10 * t_max, 0.0, 1.0]
    popt, _ = curve_fit(rabi_model, tlist, pops, p0=p0, maxfev=5000)
    omega_fit = abs(popt[0])
    t_pi_cal = np.pi / omega_fit
    return t_pi_cal, omega_fit, tlist, pops, popt


def main():
    T1_DEFAULT, T2_DEFAULT = 100.0, 75.0  # long compared to pulse timescales (~0.5s)

    # --- One example calibration run, and the payoff of calibrating at all ---
    t_pi_cal, omega_fit, tlist, pops, popt = calibrate_pi_pulse(T1_DEFAULT, T2_DEFAULT, n_shots=200)
    t_pi_nominal = np.pi / OMEGA_NOMINAL

    fid_uncalibrated = true_population(OMEGA_TRUE, t_pi_nominal, T1_DEFAULT, T2_DEFAULT)
    fid_calibrated = true_population(OMEGA_TRUE, t_pi_cal, T1_DEFAULT, T2_DEFAULT)
    print(f"true Rabi frequency:      {OMEGA_TRUE / (2 * np.pi):.4f} Hz")
    print(f"fitted Rabi frequency:    {omega_fit / (2 * np.pi):.4f} Hz")
    print(f"nominal (uncalibrated) pi-pulse fidelity: {fid_uncalibrated:.4f}")
    print(f"calibrated pi-pulse fidelity:              {fid_calibrated:.4f}")
    assert fid_calibrated > 0.99, "calibration should recover a near-perfect pi-pulse"
    assert fid_calibrated > fid_uncalibrated, "calibration must beat blindly using the nominal pulse"

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(tlist, pops, "o", alpha=0.6, label="noisy measurements (200 shots/point)")
    fine_t = np.linspace(0, tlist[-1], 400)
    ax.plot(fine_t, rabi_model(fine_t, *popt), "-", label="fitted Rabi model")
    ax.axvline(t_pi_nominal, color="gray", linestyle="--", label="nominal pi-pulse (uncalibrated)")
    ax.axvline(t_pi_cal, color="red", linestyle="--", label="calibrated pi-pulse")
    ax.set_xlabel("drive duration (s)")
    ax.set_ylabel(r"population in $|1\rangle$")
    ax.set_title("Rabi calibration recovers the true pulse duration")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/step5_calibration_curve.png", dpi=150)
    print(f"saved plot to {OUTPUT_DIR}/step5_calibration_curve.png")

    # --- Calibration accuracy vs. number of measurement shots ---
    # Isolated from decoherence (T1=T2=inf) so the only noise source is
    # finite-shot (binomial) sampling of the calibration sweep itself.
    shot_counts = [3, 10, 30, 100, 300, 1000]
    n_trials = 15
    mean_infid, std_infid = [], []
    for n_shots in shot_counts:
        trial_infid = []
        for _ in range(n_trials):
            t_pi_cal, _, _, _, _ = calibrate_pi_pulse(np.inf, np.inf, n_shots)
            trial_infid.append(1 - true_population(OMEGA_TRUE, t_pi_cal, np.inf, np.inf))
        mean_infid.append(np.mean(trial_infid))
        std_infid.append(np.std(trial_infid))
    mean_infid, std_infid = np.array(mean_infid), np.array(std_infid)

    print("shots -> mean post-calibration infidelity:")
    for n, m in zip(shot_counts, mean_infid):
        print(f"  {n:5d} -> {m:.5f}")
    assert mean_infid[0] > mean_infid[-1], "more shots should yield a more accurate calibration"

    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.errorbar(shot_counts, mean_infid, yerr=std_infid, marker="o")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("shots per calibration point")
    ax2.set_ylabel("post-calibration infidelity")
    ax2.set_title(f"Calibration accuracy vs. shot noise, no decoherence ({n_trials} trials/point)")
    fig2.tight_layout()
    fig2.savefig(f"{OUTPUT_DIR}/step5_accuracy_vs_shots.png", dpi=150)
    print(f"saved plot to {OUTPUT_DIR}/step5_accuracy_vs_shots.png")

    # --- Calibration accuracy vs. decoherence (T1, with T2 = 0.75*T1) ---
    T1_values = np.array([1.0, 2.0, 5.0, 10.0, 20.0, 50.0])
    n_shots_fixed = 300
    n_trials_t1 = 10
    mean_infid_t1 = []
    for T1 in T1_values:
        T2 = 0.75 * T1
        trial_infid = [
            1 - true_population(OMEGA_TRUE, calibrate_pi_pulse(T1, T2, n_shots_fixed)[0], T1, T2)
            for _ in range(n_trials_t1)
        ]
        mean_infid_t1.append(np.mean(trial_infid))
    mean_infid_t1 = np.array(mean_infid_t1)

    print("T1 -> mean post-calibration infidelity:")
    for t1, m in zip(T1_values, mean_infid_t1):
        print(f"  {t1:5.1f} -> {m:.5f}")
    assert mean_infid_t1[0] > mean_infid_t1[-1], "shorter T1 should limit achievable calibration accuracy"

    fig3, ax3 = plt.subplots(figsize=(7, 4))
    ax3.plot(T1_values, mean_infid_t1, "o-")
    ax3.set_xscale("log")
    ax3.set_yscale("log")
    ax3.set_xlabel(r"$T_1$ (s)")
    ax3.set_ylabel("post-calibration infidelity")
    ax3.set_title(f"Decoherence sets a floor on calibration accuracy ({n_shots_fixed} shots/point)")
    fig3.tight_layout()
    fig3.savefig(f"{OUTPUT_DIR}/step5_accuracy_vs_t1.png", dpi=150)
    print(f"saved plot to {OUTPUT_DIR}/step5_accuracy_vs_t1.png")


if __name__ == "__main__":
    main()
