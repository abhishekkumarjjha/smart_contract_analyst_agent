# Skill: /analyze-contract

## What This Skill Does

`/analyze-contract` is a Claude Code slash command that runs the full clinical trial contract analysis pipeline from the command line. It is the Claude Code interface to the same logic powering the Streamlit app — useful for batch processing, CI integration, or analyst workflows where a UI is not needed.

## Usage

```bash
/analyze-contract <path-to-contract.pdf> [--study-type <type>] [--output json|markdown]
```

### Examples

```bash
# Auto-classify study type and analyze
/analyze-contract contracts/pfizer_ra_study_2026.pdf

# Override study type if you already know it
/analyze-contract contracts/astrazeneca_copd_trial.pdf --study-type Pulmonology

# Output as JSON for downstream processing
/analyze-contract contracts/novo_diabetes_study.pdf --study-type Endocrinology --output json
```

## What It Returns

```
CLINICAL CONTRACT ANALYSIS
==========================
Study Type:      Pulmonology (confidence: 91%)
Contract:        astrazeneca_copd_trial.pdf
Master Items:    7 standard billing items loaded

MISSING BILLING ITEMS (3 found missing)
----------------------------------------
❌ Screen Failure Fee          — $650/occurrence  [MISSING]
❌ Induced Sputum Processing   — $400/sample      [MISSING]
❌ Regulatory Document Fee     — $2,000 startup   [MISSING]

Estimated revenue gap: $3,050 + per-patient screen failure exposure

FLAGGED CLAUSES (2 identified)
--------------------------------
🚩 HIGH   — Payment Trigger Clause
   Sponsor requires internal approval before releasing payment,
   creating 90+ day payment delays with no penalty to sponsor.
   → Negotiate: payment triggered by visit completion, net 30.

🚩 MEDIUM — Unilateral Amendment Rights
   Sponsor can modify protocol and budget without site consent.
   → Negotiate: material budget changes require written site agreement.

EXECUTIVE SUMMARY
-----------------
This contract has significant billing gaps totaling an estimated $3,050
in recoverable startup revenue plus per-patient screen failure exposure.
The payment trigger clause is the highest priority negotiation item.
Recommend returning to sponsor with redlined billing schedule before execution.
```

## Pipeline (What Happens When You Run It)

```
/analyze-contract contract.pdf
        │
        ▼
1. PDF TEXT EXTRACTION
   PyPDF2 extracts raw text from all pages
        │
        ▼
2. STUDY CLASSIFICATION  [Claude]
   Claude reads first 3,000 chars and classifies therapeutic area
   Returns: study_type, confidence %
        │
        ▼
3. MASTER LIST LOAD  [deterministic]
   billing_master.py returns standard items for this study type
   No LLM involved — this is institutional knowledge, not inference
        │
        ▼
4. BILLING DIFF  [Claude]
   Claude scans full contract for each master item
   Handles semantic variation: "screen failure" ≠ "screening reimbursement"
   Returns: found[], missing[]
        │
        ▼
5. CLAUSE ANALYSIS  [Claude]
   Claude identifies sponsor-favorable clauses with risk ratings
   Returns: flagged_clauses[], executive summary
        │
        ▼
6. AUDIT LOG
   Every run logged with inputs, classifications, and findings
   Traceable to source document — required for compliance environments
```

## Why This Is a Skill, Not Just a Prompt

A Claude Code Skill packages this pipeline as a repeatable, parameterized command that:

- **Enforces the mapping rules deterministically** — the category-to-billing-list mapping is code, not inference. Claude cannot hallucinate items onto the master list.
- **Maintains the audit trail** — every run is logged with the source document, classification, and findings. You cannot get this from a raw Claude conversation.
- **Is composable** — this Skill can be called by a sub-agent or chained with `/generate-redline` to produce a negotiation-ready contract revision.
- **Is institutional memory** — the billing master grows with every contract reviewed. The Skill gets smarter as the data layer grows, without retraining anything.

## Composing With Other Skills

```bash
# Chain: analyze → generate redline → email to sponsor
/analyze-contract contract.pdf --output json | /generate-redline | /draft-email --to sponsor@pharma.com
```

## Configuration

The Skill reads from `~/.claude/settings.json`:

```json
{
  "skills": {
    "analyze-contract": {
      "default_output": "markdown",
      "audit_log_path": "./logs/contract_analysis.jsonl",
      "billing_master_path": "./billing_master.py",
      "soul_path": "./docs/soul.md"
    }
  }
}
```
