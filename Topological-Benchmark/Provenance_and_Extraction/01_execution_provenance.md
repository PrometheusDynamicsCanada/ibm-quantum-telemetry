# Execution Provenance: T1 Relaxation and the Routing Anomaly

To ensure a mathematically valid A/B test without transient hardware drift, both the SABRE baseline and the Prometheus-shielded circuit were batched into a single `SamplerV2` array and submitted simultaneously to `ibm_kingston`.

### 1. Array Index Provenance
IBM's Qiskit Runtime API strictly preserves the index order of submitted PUBs (Primitive Unified Builders). The execution payload was structured as follows:

\`\`\`python
job = sampler.run([sabre_baseline, physical_circuit])
\`\`\`
* **PUB 0 (Index 0):** Unshielded SABRE Baseline (Optimization Level 3)
* **PUB 1 (Index 1):** Prometheus v15 PCA-Dynamics Matrix

### 2. Topological Verification & The Depth Penalty
Reviewers unpacking the `job-info.json` payload can independently verify the compiler attribution by observing the physical gate depths stored in the Base64-encoded QPY circuits. (See `verify_pubs.py` in the Ledger folder for automated extraction).
* **PUB 0 (SABRE):** Physical Depth: 42. Optimized for minimal gate count.
* **PUB 1 (Prometheus):** Physical Depth: 346. Intentionally bloated with SWAP gates to preserve global entanglement topologies.

### 3. The Thermodynamic Output (T1 Relaxation)
The logical blueprint contains complex phase rotations designed to generate a highly distributed, living quantum state. 
* **The SABRE Collapse:** Despite its shallow depth of 42, SABRE's physical output suffered catastrophic T1 relaxation, returning a massive spike of 555 shots at the ground state (`0x0000`). The entanglement structure completely failed.
* **The Prometheus Shield:** Despite a massive 8x physical depth penalty (346 depth), Prometheus successfully insulated the wave against T1 decay, distributing the signal across the intended complex states and preventing ground-state collapse.