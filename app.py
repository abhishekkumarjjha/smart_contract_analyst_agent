import streamlit as st
import PyPDF2
from agent import ContractAgent

st.set_page_config(page_title="Clinical Contract Analyzer", page_icon="⚕️", layout="wide")

st.title("⚕️ Clinical Trial Contract Analyzer")
st.markdown(
    "Upload a clinical trial agreement. The agent classifies the study, loads the master "
    "billing list for that therapeutic area, diffs it against the contract, and flags every "
    "clause where the sponsor is underpricing your site."
)

with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Anthropic API Key", type="password")
    st.markdown("---")
    st.markdown("**Pipeline**")
    st.markdown(
        "1. Upload contract PDF or paste text\n"
        "2. Agent classifies therapeutic area\n"
        "3. Loads master billing list for that area\n"
        "4. Diffs contract vs. master list\n"
        "5. Flags missing items + risky clauses\n"
        "6. Outputs audit-ready report"
    )

if not api_key:
    st.warning("Enter your Anthropic API key in the sidebar to begin.")
    st.stop()

tab1, tab2 = st.tabs(["📄 Upload PDF", "📝 Paste Text"])
contract_text = None

with tab1:
    uploaded = st.file_uploader("Upload contract (PDF)", type=["pdf"])
    if uploaded:
        try:
            reader = PyPDF2.PdfReader(uploaded)
            contract_text = "\n".join(
                page.extract_text() for page in reader.pages if page.extract_text()
            )
            st.success(f"Extracted {len(contract_text):,} characters from {len(reader.pages)} pages.")
        except Exception as e:
            st.error(f"PDF extraction failed: {e}")

with tab2:
    pasted = st.text_area("Paste contract text", height=300)
    if pasted.strip():
        contract_text = pasted.strip()

if contract_text:
    st.markdown("---")
    if st.button("🔍 Analyze Contract", type="primary", use_container_width=True):
        agent = ContractAgent(api_key=api_key)

        with st.spinner("Step 1/4 — Classifying therapeutic area..."):
            study_type, confidence = agent.classify_study(contract_text)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"**Study Type:** {study_type}")
        with col2:
            st.metric("Confidence", f"{confidence}%")

        with st.spinner(f"Step 2/4 — Loading master billing list for {study_type}..."):
            master_items = agent.load_master_list(study_type)
        st.success(f"Loaded {len(master_items)} standard billing items.")

        with st.spinner("Step 3/4 — Scanning contract for billing items..."):
            found_items, missing_items = agent.diff_billing_items(contract_text, master_items)

        with st.spinner("Step 4/4 — Flagging clauses and generating recommendations..."):
            analysis = agent.analyze_contract(contract_text, study_type, missing_items)

        st.markdown("---")
        st.header("📋 Results")

        # Missing items
        st.subheader(f"🔴 Missing Billing Items ({len(missing_items)})")
        if missing_items:
            st.caption(
                "These items appear in the master list for this study type but are absent "
                "from the contract. Sponsors commonly omit these to reduce site payouts."
            )
            for item in missing_items:
                with st.expander(f"➕ {item['name']} — ${item['typical_rate']:,} per {item['unit']}"):
                    st.markdown(f"**Category:** {item['category']}")
                    st.markdown(f"**Why sponsors omit this:** {item['rationale']}")
                    st.markdown(f"**Recommended contract language:**\n\n> {item['suggested_language']}")
        else:
            st.success("All standard billing items are present.")

        # Found items
        st.subheader(f"✅ Items Found in Contract ({len(found_items)})")
        cols = st.columns(3)
        for i, item in enumerate(found_items):
            cols[i % 3].markdown(f"- {item}")

        # Flagged clauses
        st.subheader("⚠️ Flagged Clauses")
        flagged = analysis.get("flagged_clauses", [])
        if flagged:
            for clause in flagged:
                with st.expander(f"🚩 {clause['risk_level']} Risk — {clause['clause_type']}"):
                    st.markdown(f"**Excerpt:** *{clause['excerpt']}*")
                    st.markdown(f"**Risk:** {clause['explanation']}")
                    st.markdown(f"**Action:** {clause['recommendation']}")
        else:
            st.success("No high-risk clauses detected.")

        # Summary
        st.subheader("📝 Executive Summary")
        st.markdown(analysis.get("summary", ""))

        # Audit trail
        with st.expander("🔎 Audit Log"):
            st.json({
                "study_type": study_type,
                "confidence_pct": confidence,
                "master_items_loaded": len(master_items),
                "items_found": len(found_items),
                "items_missing": len(missing_items),
                "clauses_flagged": len(flagged),
            })
