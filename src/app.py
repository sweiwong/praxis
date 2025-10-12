"""
PRAXIS Streamlit Web Application

Interactive UI for generating evidence-based MSK rehabilitation protocols.
"""

import streamlit as st
from main import PraxisMVP
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
# SIDEBAR: COMMON MSK CONDITIONS
# =============================================================================

st.sidebar.header("📚 Common MSK Conditions")
st.sidebar.markdown("Click any condition to auto-fill:")

# Predefined condition buttons organized by category
common_conditions = {
    "Knee": [
        "ACL reconstruction rehabilitation",
        "Meniscus repair rehabilitation",
        "Patellar tendinopathy",
        "Patellofemoral pain syndrome",
    ],
    "Shoulder": [
        "Rotator cuff tendinopathy",
        "Rotator cuff repair rehabilitation",
        "Shoulder impingement syndrome",
        "Labral tear rehabilitation",
    ],
    "Back": [
        "Low back pain",
        "Lumbar disc herniation",
        "Lumbar spinal stenosis",
    ],
    "Foot/Ankle": [
        "Ankle sprain rehabilitation",
        "Plantar fasciitis",
        "Achilles tendinopathy",
    ],
    "Elbow/Wrist": [
        "Tennis elbow (lateral epicondylitis)",
        "Golfer's elbow (medial epicondylitis)",
        "Wrist tendinopathy",
    ],
    "Hip": [
        "Hip femoroacetabular impingement",
        "Gluteal tendinopathy",
        "Hip labral tear rehabilitation",
    ]
}

# Initialize session state for selected condition
if 'selected_condition' not in st.session_state:
    st.session_state.selected_condition = ""

# Display condition buttons by category
for category, conditions in common_conditions.items():
    st.sidebar.subheader(category)
    for condition in conditions:
        if st.sidebar.button(condition, key=f"btn_{condition}"):
            st.session_state.selected_condition = condition
            st.rerun()

# =============================================================================
# SIDEBAR: SETTINGS
# =============================================================================

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Settings")

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

# =============================================================================
# SIDEBAR: ABOUT
# =============================================================================

st.sidebar.markdown("---")
st.sidebar.header("ℹ️ About PRAXIS")
st.sidebar.markdown("""
PRAXIS is an open-source AI research agent that:
- Searches PubMed for MSK research
- Grades evidence quality
- Generates rehab protocols
- Provides clinician-ready guidelines

**Built with:**
- Claude (Anthropic)
- PubMed API
- Streamlit

**Created by:** Wei Wong
**GitHub:** [sweiwong/praxis](https://github.com/sweiwong/praxis)
""")

# =============================================================================
# MAIN CONTENT: CONDITION INPUT
# =============================================================================

st.markdown("---")
st.header("🔍 Enter MSK Condition")

# Text input for custom condition (use session state value if button clicked)
condition_input = st.text_input(
    "Condition or injury:",
    placeholder="e.g., ACL reconstruction, rotator cuff tear, patellar tendinopathy",
    value=st.session_state.selected_condition,
    help="Enter any musculoskeletal condition or injury"
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
    # Validate input
    if not condition_input:
        st.error("⚠️ Please enter an MSK condition")
    else:
        # Show loading spinner with custom message
        with st.spinner(f"🔍 Researching {condition_input}... This may take 30-60 seconds..."):
            try:
                # Generate protocol
                result = st.session_state.praxis.generate_protocol(
                    condition=condition_input,
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
                            file_name=f"praxis_protocol_{condition_input.replace(' ', '_')}.md",
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
                            file_name=f"praxis_sources_{condition_input.replace(' ', '_')}.md",
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
