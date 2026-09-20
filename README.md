# Quantum Control Simulation Project

A software-only project simulating quantum bit control, calibration, and noise — built with QuTiP. The goal is to demonstrate hands-on understanding of the classical control problems behind quantum hardware, relevant to research on scalable, modular quantum control architectures.

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

## Notes

- No physical hardware required — this is a fully simulated, software-only project.
- Each step should produce a runnable script or notebook plus a short note on what was learned.
- The final writeup is the most important deliverable — it's what turns this from "a coding exercise" into something worth sharing.
