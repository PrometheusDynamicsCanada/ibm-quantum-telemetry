# Prometheus Quantum Compiler: Empirical Telemetry & Hardware Benchmarks

### Executive Summary
This repository contains the broader hardware telemetry program evaluating Prometheus, an experimental routing pipeline designed around hardware-aware physical placement. 

**How does the effect scale, and where does the routing penalty dominate?**

Our experiments indicate that minimizing physical 2Q gate count and circuit depth is not always sufficient to maximize fidelity on a real superconducting QPU. Across controlled hardware executions on IBM processors, we observe cases in which Prometheus intentionally generated substantially more routing operations than conventional compilation while producing output distributions with stronger agreement with the ideal logical computation.

The observed advantage is not universal. At sufficiently large problem sizes, the measured fidelity advantage disappears, and the additional routing cost is no longer compensated by the observed placement advantage. The resulting picture is therefore not: *"More gates are better."* It is: **"Routing cost and hardware fidelity can become decoupled when routing changes the physical placement of the computation."**

---

### Central Finding
> **Physical routing cost is an incomplete proxy for execution quality on the tested hardware.**
>
> $$\Delta C_{\mathrm{routing}} > 0, \quad \Delta F_H > 0$$

---

#### Results-at-a-Glance
| Benchmark Domain | Key Result |
| :--- | :--- |
| **Micro-Gradient (Repo 2)** | +242 2Q gates / +0.1197 Hellinger fidelity vs SABRE O3 |
| **Randomized (Repo 3)** | 75% win rate vs SABRE O3 (30 of 40 matched instances) |
| **100,000-Shot Validation** | 16.61% vs 3.19% Top-5 retention (+13.42 pp; 5.21×) despite +784 2Q gates |
| **Scaling Boundaries** | Observed routing penalty eventually dominates the placement-associated advantage |

### 1. Experimental Design & Hardware Scope
* **Primary Hardware:** `ibm_marrakesh` (with high-shot validation executed on alternative hardware topologies)
* **Architecture:** IBM Heron (156-qubit)
* **Comparators:** Qiskit SABRE (Optimization Level 3) and TKET
* **Pipeline Evaluated:** Prometheus (experimental routing pipeline)

### 2. Scaling Matrix & Failure Boundaries
The broader telemetry program sweeps QFT, GHZ, QAOA, and CrossEnt across multiple circuit sizes to establish where the physical placement advantage breaks down.

At $N=6$ through $N=9$, we observe **fidelity-rescue regimes** (e.g., QAOA-6 at +0.1627 vs SABRE O3, QAOA-9 at +0.1461 vs SABRE O3). At larger circuit sizes, the measured fidelity advantage disappears, and the additional routing cost is no longer compensated by the observed placement advantage. 

In the tested data, $N=10$ provides a clear example of this transition for QAOA and QFT. Dense CrossEnt workloads reach the same empirical crossover regime at smaller scales. This is important because it provides a falsifiable operating regime rather than an unrestricted performance claim.

### 3. Supplementary Evidence: Distribution-Level Signal Concentration
A separate 5-qubit EfficientSU2 experiment examined whether the compiler's physical mapping could affect concentration around an intended output state.

| Pipeline | Target-state extraction | Top-5 retention |
| :--- | :--- | :--- |
| **SABRE O3** | 688 / 2,000 | 688 / 2,000 |
| **Prometheus** | 915 / 2,000 | 1,861 / 2,000 |

The purpose of this supplementary experiment is to provide an additional example in which two semantically equivalent physical implementations produce materially different hardware output distributions, supporting the central observation.

### 4. 100,000-Shot Distribution Validation
A 100,000-shot execution was used to assess whether the observed distributional separation remains visible at substantially higher sampling resolution for an 8-qubit hardware benchmark (`circuit-345`).

| Metric | SABRE O3 | Prometheus | $\Delta$ |
| :--- | :--- | :--- | :--- |
| **Physical depth** | 183 | 1,282 | **+1,099** |
| **Physical 2Q gates** | 91 | 875 | **+784** |
| **Shannon entropy** | 7.9554 | 6.6045 | **-1.3509** |
| **Dominant peak (Top-1)** | 0.70% | 4.52% | **+3.82%** |
| **Top-5 retention** | 3.19% | 16.61% | **+13.42%** |

The experiment placed both compiler outputs within the same SamplerV2 execution structure (**Job ID:** `d8mi6lbqv2lc7387o3kg`), reducing confounding from temporal calibration drift. Despite executing nearly 10x the physical 2Q gate volume, the Prometheus mapping increased Top-5 retention from 3.19% to 16.61% (5.21×). 

Prometheus produced a substantially lower output entropy (7.9554 → 6.6045) while simultaneously increasing dominant-state probability and Top-5 retention, indicating increased concentration in the measured output distribution rather than entropy reduction alone being treated as a fidelity metric. This validation is intentionally distributional rather than a standalone fidelity claim: entropy, Top-1 probability, and Top-5 retention characterize output concentration, while the primary experiments (Repositories 1 & 2) use Hellinger fidelity against the exact ideal distribution.

### 5. What the Data Actually Imply
The evidence suggests that physical routing cost is an incomplete proxy for execution quality on the tested hardware.

A compiler may need to consider not only *how much routing does this solution require?* but also *where does the resulting computation execute?* This suggests a broader compiler objective in which routing cost and physical hardware quality are jointly optimized:

$$ C = \alpha C_{\mathrm{routing}} + \beta C_{\mathrm{depth}} + \gamma C_{\mathrm{hardware}} $$

The experiments do not establish the correct coefficients. They demonstrate why such an objective deserves experimental investigation.

### 6. Central Scientific Conclusion
Across the tested IBM Heron workloads, physical routing cost was not a sufficient predictor of measured hardware distribution quality. We observed matched logical circuits in which a higher-cost physical realization produced a higher measured distribution-quality metric, including higher Hellinger fidelity in the primary benchmarks and substantially greater target-state concentration in the 100,000-shot validation. 

The observed crossover with increasing circuit size indicates that the effect is regime-dependent rather than a universal advantage of additional routing. The results therefore motivate treating physical placement and routing cost as potentially distinct optimization variables in hardware-aware quantum compilation.

### 7. The Industry-Relevant Question
The ultimate question is not whether Prometheus should replace SABRE or TKET. It is whether quantum compilers should treat physical routing as a purely combinatorial optimization problem. The experimental evidence motivates a different question:

**Can hardware-aware compilation predict when a more expensive physical route produces a better overall execution than the minimum-cost route?**

Prometheus is not presented here as the answer to that question; it is an experimental system demonstrating why the question exists.

---

### 8. Data Provenance & File Ledger
To ensure complete independent reproducibility without requiring trust in the Prometheus compiler implementation, the raw execution payloads downloaded directly from IBM Quantum are provided in the `/data/` directory.

| Experiment | IBM Job | Hardware | Shots | Primary artifact |
| :--- | :--- | :--- | :--- | :--- |
| **100k validation / circuit-345** | `d8mi6lbqv2lc7387o3kg` | `[exact backend]` | 100,000 | `*-result.json` |
| **100k validation / circuit-131** | `d8mgthr2d42s73cclap0` | `[exact backend]` | 100,000 | `*-result.json` |

*Note: Extract the zipped JSON logs to recalculate the reported distributions natively.*
