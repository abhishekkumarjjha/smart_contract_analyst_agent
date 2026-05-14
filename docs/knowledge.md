# Clinical Trial Domain Knowledge

This file encodes the domain knowledge the agent draws on when analyzing contracts.
It is the difference between a generic LLM and a specialist — Claude reads this
context to reason accurately about clinical research contracts.

---

## The Clinical Trial Contract Ecosystem

### Who the Parties Are

**Sponsor** — the pharmaceutical, biotech, or medical device company funding the trial.
Their goal: get the drug approved as cheaply as possible. Contract teams are incentivized
to minimize site payments.

**CRO (Contract Research Organization)** — often acts as intermediary between sponsor
and site. Adds a markup layer and sometimes further compresses site budgets.

**Investigative Site** — the hospital, clinic, or research center running the trial.
Bears the operational cost: staff time, equipment, regulatory burden, and patient care.
The site's budget negotiation directly determines whether it can afford to run the trial
without subsidizing the sponsor.

**IRB (Institutional Review Board)** — independent ethics committee that approves the
protocol. IRB fees must be in the budget. Sponsors sometimes omit IRB amendment fees.

---

## The Budget Structure

A clinical trial budget has three components:

### 1. Per-Visit Fees
Payment for each protocol-required patient visit. Includes:
- Physician/investigator time
- Coordinator time
- Procedure fees (labs, imaging, assessments)
- Drug administration

**Common sponsor tactic:** Bundle procedures into a single visit fee that does not
cover actual cost. Example: pricing a visit with spirometry + induced sputum + safety
labs at $800 when true cost is $1,300.

### 2. Per-Patient Fees
- **Enrollment fee** — paid when a patient signs consent
- **Screen failure fee** — paid when a patient completes screening but fails eligibility
- **Completion fee** — paid when a patient completes the full protocol
- **Early termination fee** — paid when a patient withdraws or is discontinued

**Common sponsor tactic:** Omit screen failure fees entirely, or cap them far below
cost. In high-failure-rate indications (oncology, neurology), this is a major revenue gap.

### 3. Startup / Administrative Fees
- **Regulatory startup fee** — covers IRB submission, protocol review, binder setup
- **Training fee** — covers staff training on protocol and EDC system
- **Close-out fee** — covers final data reconciliation and regulatory submission

**Common sponsor tactic:** Omit startup fees entirely or offer a token amount ($500)
that covers less than 10% of actual coordinator time.

---

## High-Risk Clause Patterns

### Payment Trigger Clauses
**What they say:** "Payment will be made within 30 days of sponsor approval of visit data."
**Why they are dangerous:** "Sponsor approval" is undefined and unilateral. Sponsors can
delay payment indefinitely by withholding data approval. Sites have no recourse.
**Standard:** Payment should trigger on visit completion and CRF submission, not sponsor approval.

### Unilateral Amendment Rights
**What they say:** "Sponsor reserves the right to modify the protocol at any time."
**Why they are dangerous:** Protocol amendments increase site workload. If the budget
cannot be renegotiated after amendments, the site absorbs the cost.
**Standard:** Material amendments that increase site burden must trigger budget renegotiation.

### Overhead Exclusion Clauses
**What they say:** "The budget is inclusive of all direct and indirect costs."
**Why they are dangerous:** Sites have institutional overhead rates (F&A rates) of
26–55%. If overhead is excluded, the site subsidizes the sponsor's trial.
**Standard:** F&A rates should be explicitly included or a separate overhead line item negotiated.

### Broad IP Assignment
**What they say:** "All inventions, discoveries, and data arising from this study are
the exclusive property of Sponsor."
**Why they are dangerous:** Sites may contribute novel findings, patient insights, or
analytical methods. Broad IP assignment transfers all value to the sponsor.
**Standard:** Site should retain rights to incidental discoveries not directly related
to the sponsor's compound.

### Publication Rights Restrictions
**What they say:** "Site may not publish study results without prior written approval from Sponsor."
**Why they are dangerous:** Indefinite publication delays suppress negative findings.
**Standard:** Sponsor review period should be capped at 60 days for comments, 90 days
for patent filing, after which the site has unconditional publication rights.

### Indemnification Imbalance
**What they say:** "Site shall indemnify Sponsor against all claims arising from
investigator negligence or protocol deviation."
**Why they are dangerous:** When written broadly, this can expose the site to liability
for sponsor-caused harm (e.g., an undisclosed drug interaction).
**Standard:** Indemnification should be mutual, with each party responsible for its
own negligence.

---

## Regulatory Framework

### ICH GCP E6(R2)
The international standard for clinical trial conduct. Key site obligations:
- Maintain investigator site file (ISF) for duration of trial + 15 years
- Report SAEs within 24 hours of awareness
- Ensure all staff are trained and documented before patient contact
- Maintain source documentation for all protocol procedures

**Budget implication:** All of the above requires staff time. If the budget does not
include regulatory maintenance fees, the site absorbs these costs.

### FDA 21 CFR Part 50 — Informed Consent
Sites must obtain written informed consent before any study procedure. Consent process
requires investigator time and coordinator documentation.
**Budget implication:** Consent visit should be a separately compensated visit, not
bundled into screening.

### FDA 21 CFR Part 54 — Financial Disclosure
Investigators with financial interests in the sponsor must disclose them. This creates
administrative burden for sites with multiple investigators.

### HIPAA — Patient Data
Clinical trial data containing PHI must be handled under a HIPAA-compliant BAA
(Business Associate Agreement). Sites should ensure the contract includes a BAA
or references an existing one.

---

## Therapeutic Area — Screen Failure Rate Benchmarks

Screen failure rates determine how much a site is exposed when screen failure fees
are omitted. Higher failure rates = higher financial risk from fee omission.

| Therapeutic Area | Typical Screen Failure Rate |
|---|---|
| Oncology | 40–60% |
| Neurology (Alzheimer's) | 50–70% |
| Cardiology | 25–40% |
| Pulmonology (COPD) | 30–50% |
| Rheumatology | 20–35% |
| Infectious Disease | 15–30% |
| Endocrinology (Diabetes) | 20–35% |
| Dermatology | 15–25% |

---

## Standard Payment Terms Reference

| Term | Sponsor-Favorable | Site-Standard |
|---|---|---|
| Payment trigger | Sponsor data approval | CRF submission |
| Payment timing | Net 60 | Net 30 |
| Screen failure fee | Omitted or capped | Full cost reimbursement |
| Overhead | Excluded | Included at institutional F&A rate |
| Amendment budget | Sponsor discretion | Mandatory renegotiation |
| Publication delay | Unlimited | 60–90 days max |

---

## Common Abbreviations

| Abbreviation | Full Term |
|---|---|
| CTA | Clinical Trial Agreement |
| CRF | Case Report Form |
| EDC | Electronic Data Capture |
| F&A | Facilities and Administrative (overhead) |
| GCP | Good Clinical Practice |
| IB | Investigator's Brochure |
| ICF | Informed Consent Form |
| IND | Investigational New Drug |
| IRB | Institutional Review Board |
| ISF | Investigator Site File |
| NOI | Notice of Intent |
| PI | Principal Investigator |
| SAE | Serious Adverse Event |
| SOP | Standard Operating Procedure |
| SUSAR | Suspected Unexpected Serious Adverse Reaction |
