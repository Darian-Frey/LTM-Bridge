# Contributing to LTM-Bridge
**Role:** Protocol Evolution & Symbolic Standardization  
**Core Principle:** Maintain Zero-Loss Integrity

Thank you for helping build the "Git for AI Context." As a contributor, you are helping define the symbolic language that allows AI agents to communicate with perfect fidelity.

## 1. The SLT Standard
All additions to the **Symbolic Lookup Table (SLT)** must follow the **Minimalist Semantic Rule**:
- **Symbol Length:** 2–4 characters only.
- **Determinism:** The mapping must be reversible and unambiguous.
- **Neutrality:** No model-specific assumptions (e.g., no "GPT_ONLY" symbols).

## 2. Proposing a New Symbol
If you identify a recurring project nuance that isn't captured by v1.2 (ALN, MR, UV, CTX, OBJ, CON, PAY, RSK, DEP, BC), follow this process:

1. **Open an Issue:** Use the tag `[SLT-PROPOSAL]`.
2. **Justification:** Provide a "Chaos Test" case where the absence of this symbol leads to context drift or logical failure.
3. **Draft the Mapping:** Propose the shortcode and the full semantic definition for the `bootstrap.json`.

## 3. Pull Request (PR) Requirements
We do not accept "Conversational" code. All PRs must maintain the SCHEMA_V5 structural integrity:
- **Documentation:** Any logic changes must be reflected in the `/specs` directory.
- **Validation:** New symbols must be integrated into the `tools/ltm_scanner.py` validation logic.
- **Testing:** Pass a "Re-hydration Audit" ensuring a sub-300 token payload footprint.

## 4. Architectural Governance
The LTM-Bridge follows a **Risk-First** hierarchy. Any contribution that prioritizes "Objective Completion" over "Risk Mitigation" will be rejected. The bridge is designed for high-stakes engineering where safety and state-integrity are paramount.

---
*By contributing, you agree that your suggestions become part of the open LTM-Bridge standard under the project's license.*
