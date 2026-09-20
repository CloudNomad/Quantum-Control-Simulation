# Step 1: Environment Setup

Installed `qutip`, `numpy`, `scipy`, `matplotlib`, and `jupyter` via pip (see `requirements.txt`).

Verified the install with `scripts/step1_environment_check.py`: a qubit starting in
`|0>` driven by a constant `sigma_x` Hamiltonian for a calibrated duration flips
fully to `|1>` (`<sigma_z>` goes from `+1` to `-1`), confirming `qutip.mesolve`
integrates the Schrodinger equation correctly.

**Versions confirmed working:** qutip 5.3.1, numpy 2.4.2, scipy 1.15.3, matplotlib 3.11.2.
