"""
PRAXIS Streamlit Web Application

Interactive UI for generating evidence-based MSK rehabilitation protocols.
"""

import streamlit as st
from main import PraxisMVP
from data import MSK_CONDITIONS
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="PRAXIS - MSK Rehab Research Agent",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS FOR BETTER STYLING
# =============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-top: 0;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# MAIN HEADER
# =============================================================================

st.markdown('<p class="main-header">🏃 PRAXIS</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Evidence-Based Musculoskeletal Rehabilitation Protocols</p>', unsafe_allow_html=True)

# Disclaimer banner
st.warning("""
⚠️ **Disclaimer**: PRAXIS is a research tool designed to assist clinical judgment.
It does not provide medical advice and should not replace professional clinical assessment,
diagnosis, or treatment. Always use clinical reasoning and consider individual patient factors.
""")

# =============================================================================
# SIDEBAR: ABOUT PRAXIS
# =============================================================================

st.sidebar.header("ℹ️ About PRAXIS")
st.sidebar.markdown("""
**PRAXIS** generates evidence-based MSK rehabilitation protocols by:

- 🔍 Searching PubMed for latest research
- 📊 Grading evidence quality (1A, 1B, 2A, etc.)
- 📋 Creating phase-based protocols with exercise progressions
- 📚 Providing research citations

**What to Expect:**
- Comprehensive rehabilitation protocols
- Evidence-graded interventions
- Dosage parameters (sets, reps, load)
- Return-to-activity criteria

**Generation Time:** 30-60 seconds per protocol
""")

# Initialize session state for selected condition (for sidebar buttons if needed later)
if 'selected_condition' not in st.session_state:
    st.session_state.selected_condition = ""

# =============================================================================
# SIDEBAR: SETTINGS
# =============================================================================

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Settings")

# Search parameters
max_articles = st.sidebar.slider(
    "Max articles to analyze",
    min_value=5,
    max_value=30,
    value=15,
    step=5,
    help="More articles = more comprehensive analysis but slower"
)

years_back = st.sidebar.slider(
    "Search years back",
    min_value=5,
    max_value=20,
    value=10,
    step=5,
    help="How many years back to search for research"
)

# Protocol customization options
st.sidebar.markdown("**Protocol Options:**")

include_education = st.sidebar.checkbox(
    "Include patient education handout",
    value=False,
    help="Generate plain-language handout for patients"
)

protocol_detail = st.sidebar.selectbox(
    "Protocol detail level",
    ["Brief", "Standard", "Comprehensive"],
    index=1,
    help="Choose how detailed the protocol should be"
)

include_red_flags = st.sidebar.checkbox(
    "Include red flags & contraindications",
    value=True,
    help="Add safety warnings and contraindications"
)

# =============================================================================
# SIDEBAR: EXPORT OPTIONS
# =============================================================================

st.sidebar.markdown("---")
st.sidebar.header("📤 Export Options")

st.sidebar.markdown("""
**After generating a protocol:**
- Download as Markdown (see tabs)
- PDF export (coming soon)
- Copy to clipboard (coming soon)
""")

# =============================================================================
# SIDEBAR: FEEDBACK
# =============================================================================

st.sidebar.markdown("---")
st.sidebar.header("💬 Feedback")

st.sidebar.markdown("**Found this protocol helpful?**")

# Star rating
rating = st.sidebar.slider(
    "Rate this protocol",
    min_value=1,
    max_value=5,
    value=3,
    help="1 = Not useful, 5 = Very useful"
)

# Feedback text area
feedback_text = st.sidebar.text_area(
    "Comments (optional)",
    placeholder="What would make this better?",
    height=80,
    help="Your feedback helps improve PRAXIS"
)

if st.sidebar.button("Submit Feedback", type="secondary"):
    if feedback_text or rating:
        st.sidebar.success("✓ Thank you for your feedback!")
        # TODO: Implement feedback storage
    else:
        st.sidebar.info("Please provide a rating or comment")

# =============================================================================
# SIDEBAR: LINKS
# =============================================================================

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Links:**
- [GitHub Repository](https://github.com/sweiwong/praxis)
- [Report an Issue](https://github.com/sweiwong/praxis/issues)
- [Documentation](https://github.com/sweiwong/praxis#readme)
""")

# =============================================================================
# MAIN CONTENT: CONDITION INPUT
# =============================================================================

st.markdown("---")
st.header("🔍 Select or Enter MSK Condition")

# Initialize session state for dropdown selection
if 'dropdown_condition' not in st.session_state:
    st.session_state.dropdown_condition = ""

# Cascading dropdowns using Phy MSK data
st.subheader("📋 Browse by Body Zone")

# Dropdown 1: Body Zone
body_zones = [""] + list(MSK_CONDITIONS.keys())
selected_body_zone = st.selectbox(
    "1️⃣ Select Body Zone:",
    body_zones,
    help="Choose the primary area of pain or injury"
)

# Dropdown 2: Pain Zone (filtered by body zone)
if selected_body_zone:
    pain_zones = [""] + list(MSK_CONDITIONS[selected_body_zone].keys())
    selected_pain_zone = st.selectbox(
        "2️⃣ Select Pain Zone:",
        pain_zones,
        help="Choose the specific location within the body zone"
    )

    # Dropdown 3: Condition (filtered by pain zone)
    if selected_pain_zone:
        conditions = [""] + MSK_CONDITIONS[selected_body_zone][selected_pain_zone]
        selected_condition = st.selectbox(
            "3️⃣ Select Condition:",
            conditions,
            help="Choose the specific condition or diagnosis"
        )

        # Store selected condition for use in protocol generation
        if selected_condition:
            st.session_state.dropdown_condition = selected_condition
            st.success(f"✓ Selected: **{selected_condition}**")
else:
    selected_pain_zone = None
    selected_condition = None

st.markdown("---")
st.subheader("✏️ Or Enter Custom Condition")

# Text input for custom condition (use session state value if button clicked)
condition_input = st.text_input(
    "Free text input:",
    placeholder="e.g., ACL reconstruction rehabilitation, rotator cuff tear, patellar tendinopathy",
    value=st.session_state.selected_condition if st.session_state.selected_condition else "",
    help="Enter any musculoskeletal condition or injury not in the dropdowns"
)

# Clear the session state after using it
if st.session_state.selected_condition:
    st.session_state.selected_condition = ""

# =============================================================================
# INITIALIZE PRAXIS (Only once per session)
# =============================================================================

if 'praxis' not in st.session_state:
    with st.spinner("Initializing PRAXIS..."):
        try:
            st.session_state.praxis = PraxisMVP()
            st.success("✓ PRAXIS initialized successfully")
        except SystemExit:
            st.error("❌ Failed to initialize PRAXIS. Please check your .env configuration.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.stop()

# =============================================================================
# GENERATE PROTOCOL BUTTON
# =============================================================================

# Center the button using columns
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    generate_button = st.button(
        "🚀 Generate Protocol",
        type="primary",
        use_container_width=True
    )

# =============================================================================
# PROTOCOL GENERATION
# =============================================================================

if generate_button:
    # Determine which input to use (dropdown takes priority)
    final_condition = st.session_state.dropdown_condition if st.session_state.dropdown_condition else condition_input

    # Validate input
    if not final_condition:
        st.error("⚠️ Please select a condition from the dropdowns or enter one in the text field")
    else:
        # Show loading spinner with custom message
        with st.spinner(f"🔍 Researching {final_condition}... This may take 30-60 seconds..."):
            try:
                # Generate protocol
                result = st.session_state.praxis.generate_protocol(
                    condition=final_condition,
                    max_articles=max_articles,
                    years_back=years_back
                )

                # Check for errors
                if "error" in result and result["error"]:
                    st.error(f"❌ {result['error']}")
                else:
                    # Success! Display results
                    st.success(f"✅ Protocol generated successfully for **{result['condition']}**")

                    # Display results in tabs
                    tab1, tab2, tab3 = st.tabs([
                        "📋 Rehabilitation Protocol",
                        "🔬 Research Analysis",
                        "📚 Sources"
                    ])

                    # =========================================================
                    # TAB 1: REHABILITATION PROTOCOL
                    # =========================================================
                    with tab1:
                        st.markdown("### 📋 Evidence-Based Rehabilitation Protocol")
                        st.markdown("---")
                        st.markdown(result["protocol"])

                        # Download button for protocol
                        st.download_button(
                            label="📥 Download Protocol (Markdown)",
                            data=result["protocol"],
                            file_name=f"praxis_protocol_{final_condition.replace(' ', '_')}.md",
                            mime="text/markdown"
                        )

                    # =========================================================
                    # TAB 2: RESEARCH ANALYSIS
                    # =========================================================
                    with tab2:
                        st.markdown("### 🔬 Research Analysis & Evidence Grading")
                        st.markdown("---")
                        st.markdown(result["analysis"])

                        # Show articles analyzed
                        st.markdown("---")
                        st.markdown(f"**Articles Analyzed:** {len(result['articles'])}")

                        # Display article summaries in expander
                        with st.expander("📄 View Article Summaries"):
                            for i, article in enumerate(result['articles'][:10], 1):
                                st.markdown(f"**{i}. {article['title']}**")
                                st.markdown(f"*{', '.join(article['authors'][:3])}{'...' if len(article['authors']) > 3 else ''}*")
                                st.markdown(f"*{article['journal']} ({article['year']})*")
                                st.markdown(f"[View on PubMed]({article['url']})")
                                st.markdown("---")

                    # =========================================================
                    # TAB 3: SOURCES
                    # =========================================================
                    with tab3:
                        st.markdown("### 📚 Research Sources")
                        st.markdown("---")

                        st.info(f"""
                        **Total Articles Found:** {len(result['pmids'])}
                        **Articles Analyzed:** {len(result['articles'])}
                        **Search Timeframe:** Last {years_back} years
                        **Evidence Types:** Systematic reviews, RCTs, clinical trials
                        """)

                        st.markdown("### PubMed Citations")

                        # Display PMIDs with clickable links
                        for i, article in enumerate(result['articles'], 1):
                            col1, col2 = st.columns([3, 1])

                            with col1:
                                st.markdown(f"**{i}. {article['title']}**")
                                st.caption(f"{article['journal']} ({article['year']})")

                            with col2:
                                st.link_button(
                                    "PubMed",
                                    article['url'],
                                    use_container_width=True
                                )

                            st.markdown("---")

                        # Export all sources
                        sources_text = "# PRAXIS Protocol Sources\n\n"
                        sources_text += f"**Condition:** {result['condition']}\n\n"
                        for i, article in enumerate(result['articles'], 1):
                            sources_text += f"{i}. {article['title']}\n"
                            sources_text += f"   {', '.join(article['authors'][:3])}\n"
                            sources_text += f"   {article['journal']} ({article['year']})\n"
                            sources_text += f"   PMID: {article['pmid']}\n"
                            sources_text += f"   {article['url']}\n\n"

                        st.download_button(
                            label="📥 Download Sources (Markdown)",
                            data=sources_text,
                            file_name=f"praxis_sources_{final_condition.replace(' ', '_')}.md",
                            mime="text/markdown"
                        )

            except Exception as e:
                st.error(f"❌ Error generating protocol: {str(e)}")
                st.exception(e)

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p><strong>PRAXIS</strong> - Evidence-Based MSK Rehabilitation Protocols</p>
    <p>Open-source AI research agent for physical therapists and movement practitioners</p>
    <p>Created by Wei Wong | <a href='https://github.com/sweiwong/praxis'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)
