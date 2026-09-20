# Quantum Control Simulation Project

A completed software simulation of quantum bit control, calibration, and noise, built with QuTiP. Starting from an idealized two-level qubit, this project measures how much realistic classical control hardware — decoherence, pulse jitter, and crosstalk — degrades gate fidelity, how much of that an automated calibration routine can recover, and how the remaining error scales from a single qubit to a small register. The aim throughout was to build hands-on, quantitative understanding of the classical control problems behind quantum hardware, directly relevant to research on scalable, modular quantum control architectures.

**[Read the full writeup](WRITEUP.md)** for results, figures, and what's next. Runnable scripts are in [`scripts/`](scripts/), per-step notes in [`notes/`](notes/), and generated plots in [`figures/`](figures/).

## Motivation

Real qubits are controlled by classical hardware (pulse generators, amplifiers, control electronics) that is imperfect — noisy, imprecise, and harder to scale as qubit count grows. This project simulates that control problem in software: driving qubits with pulses, dealing with realistic noise and crosstalk, and building calibration routines to compensate for hardware imperfection.

## Goals

- Understand and simulate basic qubit control (Rabi driving, pulse shaping)
- Model realistic hardware imperfections (decoherence, pulse jitter, crosstalk)
- Build a working calibration routine that compensates for those imperfections
- Extend to a small multi-qubit system to explore how control complexity scales
- Document findings in a short research-style writeup

## Tech Stack

- Python 3.10+
- [QuTiP](https://qutip.org/) — quantum toolbox for simulating open quantum systems
- Jupyter (for interactive exploration and plotting)
- NumPy / Matplotlib

## Roadmap

### 1. Environment Setup
- Install Python, QuTiP (`pip install qutip`), and Jupyter
- Verify install by running a basic QuTiP example

### 2. Core Qubit Model
- Represent a qubit as a two-level system (`Qobj`, `sigmax`/`sigmay`/`sigmaz`)
- Simulate free evolution with `mesolve`
- Plot state evolution to confirm correct behavior

### 3. Basic Control Pulse (Rabi Drive)
- Apply a time-dependent microwave drive to the qubit
- Visualize the state rotating on the Bloch sphere
- Confirm a calibrated "pi-pulse" fully flips the qubit state

### 4. Realistic Noise and Imperfections
- Add decoherence via collapse operators (T1/T2 relaxation)
- Introduce pulse amplitude and timing jitter
- Add crosstalk between control channels (relevant once multiple qubits are involved)

### 5. Calibration Routine
- Implement an automated method to find correct pulse parameters (e.g., amplitude/duration search or Rabi-oscillation fitting)
- Measure calibration accuracy under different noise levels
- This is the "hardware architecture" core of the project — controlling imperfect hardware, not just simulating ideal physics

### 6. Multi-Qubit Scaling
- Extend to 2–3 qubits with shared control lines and crosstalk
- Explore how calibration difficulty and fidelity degrade as qubit count increases
- This connects directly to research on scalable, modular quantum control hardware

### 7. Writeup
- Problem statement
- Approach and methodology
- Results (plots, fidelity numbers, calibration accuracy vs. noise)
- What you'd explore next

## Key Findings

- **Calibration recovers most of what hardware imperfection costs.** Fitting a Rabi curve to noisy, finite-shot measurements of a qubit with an unknown (7%-off) drive frequency raised gate fidelity from 98.44% (nominal, uncalibrated pulse) to 99.63%.
- **Decoherence sets a hard ceiling calibration can't lift.** Pi-pulse fidelity fell from 99.8% to 80% as T1/T2 shrank toward the pulse duration — only faster pulses or longer-lived qubits fix this, not better calibration.
- **Control jitter costs fidelity roughly quadratically.** Random pulse amplitude/timing jitter cost ~0.6% fidelity at 5% jitter and ~8.9% at 20% jitter, consistent with small-angle-error scaling.
- **Crosstalk falls off as 1/detuning².** A leaked drive onto a neighboring qubit matched the analytic off-resonant-driving formula almost exactly across four orders of magnitude of frequency spacing.
- **The crosstalk error budget scales with register size — and the scaling is a design choice.** Crowding qubits onto the same frequency spacing makes total crosstalk error grow linearly with qubit count; spreading them over more spectrum as the register grows makes it saturate instead.

No physical hardware was used — this is a fully simulated, software-only project. See the [full writeup](WRITEUP.md) for methodology, plots, and what's next, and [`notes/`](notes/) for a per-step breakdown of what was learned.
