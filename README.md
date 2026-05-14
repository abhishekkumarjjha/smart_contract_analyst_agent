# Clinical Trial Contract Analyzer — Claude-Powered Agentic Pipeline

A production-deployed AI agent that analyzes clinical trial agreements, identifies missing billing items by therapeutic area, and flags sponsor-favorable clauses — compressing a full day of manual contract review to seconds.

**Built at Horizon Clinical Research Group.** This is not a side project. It was deployed in an active clinical research environment where the output directly informed contract negotiations with pharmaceutical sponsors (Pfizer, AstraZeneca, and others). Every missing billing item it surfaces is recoverable revenue.

---

## The Problem It Solves

Clinical research sites receive trial contracts from sponsors whose legal teams are paid to minimize site payments. A standard clinical trial contract review requires a financial analyst to:

1. Read 40–80 pages of dense legal and clinical language
2. Cross-reference a master billing list of standard items for that therapeutic area
3. Identify every item the sponsor has omitted or underpriced
4. Flag clauses that shift risk to the site (payment triggers, unilateral amendments, IP grabs)

This takes 4–8 hours per contract. Sites manage 10–40 concurrent trials. The analyst bottleneck is constant.

**This agent compresses that workflow to under 60 seconds.**

---

## Why Not Just Use Claude Directly?

This is the right question. Raw Claude cannot do this job for four reasons:

1. **It doesn't know your master billing list.** The agent's `billing_master.py` encodes standard billing items for 8 therapeutic areas — 50+ items with typical rates, rationale, and negotiation language. This is institutional knowledge. Claude cannot infer it.

2. **It enforces deterministic mapping rules.** `if study == pulmonology → load pulmonology billing items`. This is code, not inference. The agent never loads the wrong list because the mapping is deterministic.

3. **It maintains an audit trail.** Every analysis is logged to a JSONL file via the post-analysis hook. In a HIPAA-compliant environment, AI-assisted decisions must be traceable. A Claude conversation produces no audit record.

4. **It is composable.** The `/analyze-contract` Skill can be chained with downstream Skills (`/generate-redline`, `/draft-email`) to produce a full negotiation package without human intervention.

---

## Architecture

```
Upload Contract (PDF / text)
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  HOOK: contract_validator.py  [pre-analysis]        │
│  Validates file type, size, readability             │
│  Fails fast before any API calls                    │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  STEP 1: CLASSIFY  [Claude]                         │
│  Reads first 3,000 chars of contract                │
│  Returns: therapeutic area + confidence %           │
│  soul.md loaded as system prompt                    │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  STEP 2: LOAD MASTER LIST  [deterministic]          │
│  billing_master.py → category lookup                │
│  No LLM — institutional knowledge, not inference    │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  STEP 3: DIFF  [Claude]                             │
│  Scans full contract for each master item           │
│  Handles semantic variation in item naming          │
│  Returns: found[], missing[]                        │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  STEP 4: CLAUSE ANALYSIS  [Claude]                  │
│  Identifies sponsor-favorable clauses               │
│  Risk-rated: HIGH / MEDIUM / LOW                    │
│  Returns: flagged_clauses[], executive summary      │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  HOOK: audit_logger.py  [post-analysis]             │
│  Appends structured JSONL record                    │
│  Logs: analyst, document, findings, model, version  │
└─────────────────────────────────────────────────────┘
         │
         ▼
    Streamlit UI  /  CLI via /analyze-contract Skill
```

---

## Claude Code Integration

### Skill: `/analyze-contract`

The Claude Code slash command packages this pipeline as a repeatable, parameterized command.

```bash
# Auto-classify and analyze
/analyze-contract contracts/pfizer_ra_study_2026.pdf

# Override study type
/analyze-contract contracts/astrazeneca_copd_trial.pdf --study-type Pulmonology

# JSON output for downstream processing
/analyze-contract contracts/novo_diabetes.pdf --output json
```

See `.claude/commands/analyze-contract.md` for full documentation.

### Hooks

| Hook | Trigger | Purpose |
|---|---|---|
| `contract_validator.py` | Pre-analysis | Validates input before any API call |
| `audit_logger.py` | Post-analysis | Writes JSONL audit record automatically |

### Settings

`.claude/settings.json` configures model, permissions, and hook paths. File write permissions are scoped to `./logs/` and `./output/` only — the agent cannot write anywhere else.

---

## File Structure

```
clinical-contract-agent/
├── app.py                          # Streamlit UI
├── agent.py                        # 4-step pipeline logic
├── billing_master.py               # Master billing items by therapeutic area
├── requirements.txt
│
├── .claude/
│   ├── settings.json               # Model, hooks, permissions config
│   └── commands/
│       └── analyze-contract.md     # /analyze-contract Skill definition
│
├── docs/
│   ├── soul.md                     # Agent identity and reasoning persona
│   ├── knowledge.md                # Clinical trial domain reference
│
└── hooks/
    ├── audit_logger.py             # Post-analysis JSONL logger
    └── contract_validator.py       # Pre-analysis input validator
```

---

## Therapeutic Areas Covered

| Area | Standard Items Encoded |
|---|---|
| Oncology | 7 items (biopsy, SAE, pharmacy prep, screen failure...) |
| Pulmonology | 7 items (spirometry, sputum, FeNO, screen failure...) |
| Cardiology | 6 items (ECG, Holter, echo, screen failure...) |
| Neurology | 6 items (cognitive assessment, LP, caregiver, screen failure...) |
| Infectious Disease | 5 items (virology, isolation, screen failure...) |
| Endocrinology | 5 items (CGM, OGTT, screen failure...) |
| Rheumatology | 5 items (joint assessment, infusion suite, screen failure...) |
| Dermatology | 6 items (photography, biopsy, PASI, screen failure...) |

---

## Setup

```bash
git clone https://github.com/abhishekkumarjjha/clinical-contract-agent.git
cd clinical-contract-agent
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=your_key_here" > .env
streamlit run app.py
```

---

## Mapping to Other Domains

The architecture — classify document → load domain-specific checklist → diff → flag deviations — is domain-agnostic. The same pattern applies to:

- **Rail tariff compliance** (Trinity use case): classify shipment type → load standard rate card → diff against negotiated tariff → flag revenue gaps
- **Insurance policy review**: classify policy type → load standard coverage checklist → flag exclusions
- **Vendor contract review**: classify vendor category → load standard SLA checklist → flag missing terms

The domain knowledge layer (`billing_master.py`) is the only thing that changes. The agent logic, the Skill, and the hooks are identical.

---

## Production Context

Built during my time as Financial Analyst at Horizon Clinical Research Group (Houston, TX). Deployed to production with direct financial consequences — output used by finance and operations teams for contract negotiation and budget reconciliation with pharmaceutical sponsors.

The agent recovered identifiable revenue on every contract it reviewed by surfacing billing items sponsors had omitted.

---

## Author

**Abhishek Kumar Jha** — AI Safety Researcher · Former xAI Red Teamer · MS Business Analytics, UT Arlington

[LinkedIn](https://linkedin.com/in/abhishekumarjha) · [GitHub](https://github.com/abhishekkumarjjha) · [Portfolio](https://avi-jha.vercel.app)
