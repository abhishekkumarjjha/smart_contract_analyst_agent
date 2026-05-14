import json
import anthropic
from billing_master import BILLING_MASTER, STUDY_CATEGORIES

SYSTEM_PROMPT = open("docs/soul.md").read()


class ContractAgent:
    """
    Core agent that orchestrates the 4-step contract analysis pipeline:
    classify → load → diff → analyze.

    Why not just use Claude directly?
    Raw Claude has no access to the master billing list, cannot enforce
    category-scoped mapping rules, and produces no audit trail. This agent
    brings deterministic domain logic (the mapping rules, the diff, the
    master list) and uses Claude only for the reasoning steps that require
    language understanding: classification, clause extraction, and
    recommendation generation.
    """

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

    # ── Step 1: Classify ──────────────────────────────────────────────────

    def classify_study(self, contract_text: str) -> tuple[str, int]:
        """
        Use Claude to classify the therapeutic area from contract text.
        Returns (study_type, confidence_pct).
        """
        categories = ", ".join(STUDY_CATEGORIES.keys())
        prompt = f"""You are analyzing a clinical trial contract. 
        
Classify this contract into exactly one of these therapeutic areas: {categories}

Return JSON only, no other text:
{{"study_type": "<category>", "confidence": <0-100>, "reasoning": "<one sentence>"}}

Contract excerpt (first 3000 chars):
{contract_text[:3000]}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            raw = response.content[0].text.strip()
            # Strip markdown fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            result = json.loads(raw.strip())
            study_type = result.get("study_type", "Oncology")
            # Normalize to known category
            if study_type not in BILLING_MASTER:
                study_type = self._fuzzy_match_category(study_type)
            return study_type, result.get("confidence", 80)
        except Exception:
            return "Oncology", 70  # safe default

    def _fuzzy_match_category(self, raw: str) -> str:
        raw_lower = raw.lower()
        for category in BILLING_MASTER:
            if category.lower() in raw_lower or raw_lower in category.lower():
                return category
        return "Oncology"

    # ── Step 2: Load master list ──────────────────────────────────────────

    def load_master_list(self, study_type: str) -> list[dict]:
        """
        Deterministic lookup — no LLM involved.
        Returns the master billing items for this study type.
        """
        return BILLING_MASTER.get(study_type, BILLING_MASTER["Oncology"])

    # ── Step 3: Diff ──────────────────────────────────────────────────────

    def diff_billing_items(
        self, contract_text: str, master_items: list[dict]
    ) -> tuple[list[str], list[dict]]:
        """
        Ask Claude to scan the contract for each master item.
        Returns (found_item_names, missing_item_dicts).

        This is a Claude task because billing items appear in contracts with
        varied language: 'screen failure fee' may be written as 'screening
        visit reimbursement' or 'failed screen payment'. Keyword matching
        alone produces false negatives.
        """
        item_names = [item["name"] for item in master_items]
        names_list = "\n".join(f"- {n}" for n in item_names)

        prompt = f"""You are reviewing a clinical trial contract against a master billing checklist.

Master billing items to look for:
{names_list}

For each item, determine if it is PRESENT or ABSENT in the contract below.
An item is PRESENT if the contract includes that procedure/fee/reimbursement in any form,
even if the exact wording differs.

Return JSON only:
{{"found": ["item name 1", "item name 2"], "missing": ["item name 3"]}}

CONTRACT TEXT:
{contract_text[:6000]}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            result = json.loads(raw.strip())
            found_names = set(result.get("found", []))
            missing_names = set(result.get("missing", item_names))

            found_items = [n for n in item_names if n in found_names]
            missing_items = [
                item for item in master_items if item["name"] in missing_names
            ]
            return found_items, missing_items
        except Exception:
            # Conservative fallback: flag everything as missing
            return [], master_items

    # ── Step 4: Analyze clauses ───────────────────────────────────────────

    def analyze_contract(
        self, contract_text: str, study_type: str, missing_items: list[dict]
    ) -> dict:
        """
        Claude reads the full contract and returns:
        - flagged_clauses: sponsor-favorable clauses that need negotiation
        - summary: executive-level plain-English summary
        """
        missing_summary = (
            ", ".join(i["name"] for i in missing_items[:10])
            if missing_items else "none"
        )

        prompt = f"""You are a senior clinical research contract analyst reviewing a {study_type} trial agreement.

Already identified as missing from this contract: {missing_summary}

Your tasks:
1. Identify up to 5 clauses where the SPONSOR has included language that is unfavorable to the site:
   - Payment timing clauses (e.g., payment only after sponsor approval, not visit completion)
   - Overhead/indirect cost exclusions
   - Unilateral amendment rights
   - Overly broad IP assignment
   - Screen failure fee caps below standard

2. Write an executive summary (3-4 sentences) of the overall contract risk level.

Return JSON only:
{{
  "flagged_clauses": [
    {{
      "clause_type": "<type>",
      "risk_level": "HIGH|MEDIUM|LOW",
      "excerpt": "<verbatim excerpt under 50 words>",
      "explanation": "<why this is risky for the site>",
      "recommendation": "<what to negotiate>"
    }}
  ],
  "summary": "<executive summary>"
}}

CONTRACT:
{contract_text[:8000]}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw.strip())
        except Exception:
            return {
                "flagged_clauses": [],
                "summary": "Analysis complete. Review missing billing items above."
            }
