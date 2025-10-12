"""
PRAXIS Main Orchestration Module

Single-agent MVP: Query → Search → Analyze → Generate
This is the core logic that coordinates PubMed search and Claude analysis.

Future: Multi-agent architecture with LangGraph
"""

from utils.pubmed import PubMedClient
from utils.claude_client import ClaudeClient
from dotenv import load_dotenv
from typing import Dict, List
import sys


class PraxisMVP:
    """
    Single-agent MVP for PRAXIS - MSK rehabilitation research agent.

    Workflow:
    1. User provides MSK condition
    2. Search PubMed for relevant research
    3. Fetch article details
    4. Analyze research with Claude (evidence grading)
    5. Generate rehabilitation protocol with Claude

    Usage:
        praxis = PraxisMVP()
        result = praxis.generate_protocol("ACL reconstruction")
        print(result["protocol"])
    """

    def __init__(self):
        """Initialize PRAXIS with PubMed and Claude clients."""
        # Load environment variables from .env file
        load_dotenv()

        # Initialize PubMed client for literature search
        self.pubmed = PubMedClient()
        print("✓ PubMed client initialized")

        # Initialize Claude client for research analysis
        try:
            self.claude = ClaudeClient()
            print("✓ Claude client initialized")
        except ValueError as e:
            print(f"❌ Failed to initialize Claude client: {e}")
            print("\nPlease ensure you have:")
            print("1. Created a .env file (copy from .env.example)")
            print("2. Added your ANTHROPIC_API_KEY to .env")
            print("3. Get your API key from: https://console.anthropic.com/")
            sys.exit(1)

    def generate_protocol(
        self,
        condition: str,
        max_articles: int = 15,
        years_back: int = 10
    ) -> Dict[str, any]:
        """
        Generate complete rehabilitation protocol for MSK condition.

        This is the main entry point for PRAXIS. It orchestrates the entire workflow:
        1. Search PubMed for research
        2. Fetch article details
        3. Analyze research with Claude
        4. Generate protocol with Claude

        Args:
            condition: MSK condition (e.g., "ACL reconstruction", "rotator cuff tear")
            max_articles: Maximum number of articles to analyze (default: 15)
            years_back: How many years back to search (default: 10)

        Returns:
            Dictionary with:
            - condition: Input condition
            - pmids: List of PubMed IDs found
            - articles: List of article details
            - analysis: Research analysis from Claude
            - protocol: Generated rehabilitation protocol
            - error: Error message (if any)

        Example:
            >>> praxis = PraxisMVP()
            >>> result = praxis.generate_protocol("patellar tendinopathy")
            >>> if "error" not in result:
            >>>     print(result["protocol"])
        """
        print(f"\n{'='*70}")
        print(f"🏃 PRAXIS: Generating protocol for {condition}")
        print(f"{'='*70}\n")

        # =====================================================================
        # STEP 1: Search PubMed for relevant research
        # =====================================================================
        print(f"🔍 Step 1: Searching PubMed...")
        print(f"   Condition: {condition}")
        print(f"   Max articles: {max_articles}")
        print(f"   Years back: {years_back}\n")

        pmids = self.pubmed.search_msk_literature(
            condition=condition,
            max_results=max_articles,
            years_back=years_back
        )

        # Check if any results found
        if not pmids:
            error_msg = f"No research found for '{condition}'. Try a different condition or check your search terms."
            print(f"❌ {error_msg}\n")
            return {
                "condition": condition,
                "error": error_msg,
                "pmids": [],
                "articles": [],
                "analysis": "",
                "protocol": ""
            }

        print(f"\n✓ Found {len(pmids)} relevant articles")
        print(f"  PMIDs: {', '.join(pmids[:5])}{'...' if len(pmids) > 5 else ''}\n")

        # =====================================================================
        # STEP 2: Fetch article details (title, abstract, authors, etc.)
        # =====================================================================
        print(f"📄 Step 2: Fetching article details...")

        articles = self.pubmed.fetch_article_details(pmids)

        if not articles:
            error_msg = "Failed to fetch article details from PubMed."
            print(f"❌ {error_msg}\n")
            return {
                "condition": condition,
                "error": error_msg,
                "pmids": pmids,
                "articles": [],
                "analysis": "",
                "protocol": ""
            }

        print(f"✓ Successfully retrieved {len(articles)} article details\n")

        # Display sample of articles found
        print("Sample articles:")
        for i, article in enumerate(articles[:3], 1):
            print(f"  {i}. {article['title'][:80]}...")
            print(f"     {article['journal']} ({article['year']})")
        print()

        # =====================================================================
        # STEP 3: Analyze research with Claude
        # =====================================================================
        print(f"🤖 Step 3: Analyzing research with Claude...")
        print(f"   Sending {len(articles)} articles to Claude for analysis...")
        print(f"   This may take 10-30 seconds...\n")

        analysis = self.claude.analyze_research(
            articles=articles,
            condition=condition
        )

        if analysis.startswith("Error"):
            error_msg = f"Claude analysis failed: {analysis}"
            print(f"❌ {error_msg}\n")
            return {
                "condition": condition,
                "error": error_msg,
                "pmids": pmids,
                "articles": articles,
                "analysis": "",
                "protocol": ""
            }

        print(f"✓ Research analysis complete\n")

        # =====================================================================
        # STEP 4: Generate rehabilitation protocol
        # =====================================================================
        print(f"📋 Step 4: Generating rehabilitation protocol...")
        print(f"   Creating phase-based protocol with exercise progressions...")
        print(f"   This may take 15-40 seconds...\n")

        protocol = self.claude.generate_protocol(
            analysis=analysis,
            condition=condition
        )

        if protocol.startswith("Error"):
            error_msg = f"Protocol generation failed: {protocol}"
            print(f"❌ {error_msg}\n")
            return {
                "condition": condition,
                "error": error_msg,
                "pmids": pmids,
                "articles": articles,
                "analysis": analysis,
                "protocol": ""
            }

        print(f"✓ Protocol generation complete!\n")

        # =====================================================================
        # SUCCESS: Return complete results
        # =====================================================================
        print(f"{'='*70}")
        print(f"✅ PRAXIS protocol generated successfully!")
        print(f"{'='*70}\n")

        return {
            "condition": condition,
            "pmids": pmids,
            "articles": articles,
            "analysis": analysis,
            "protocol": protocol
        }


# =============================================================================
# MAIN EXECUTION FOR TESTING
# =============================================================================

def main():
    """
    Test the MVP with sample MSK conditions.

    Run this file directly to test PRAXIS:
        python3 src/main.py
    """
    print("\n" + "="*70)
    print("PRAXIS MVP - Musculoskeletal Rehabilitation Protocol Generator")
    print("="*70)

    # Create PRAXIS MVP instance
    try:
        praxis = PraxisMVP()
    except SystemExit:
        # Exit if initialization failed
        return

    # Test conditions (uncomment to test different conditions)
    test_conditions = [
        "ACL reconstruction rehabilitation",
        # "rotator cuff tendinopathy",
        # "patellar tendinopathy",
    ]

    # Test first condition
    condition = test_conditions[0]

    # Generate protocol
    result = praxis.generate_protocol(condition, max_articles=10)

    # Display results
    if "error" in result and result["error"]:
        print(f"\n❌ Error: {result['error']}")
    else:
        # Print summary
        print("\n" + "="*70)
        print(f"RESULTS SUMMARY")
        print("="*70)
        print(f"Condition: {result['condition']}")
        print(f"Articles analyzed: {len(result['articles'])}")
        print(f"PMIDs: {', '.join(result['pmids'][:5])}...")

        # Print analysis
        print("\n" + "="*70)
        print("RESEARCH ANALYSIS")
        print("="*70)
        print(result['analysis'])

        # Print protocol
        print("\n" + "="*70)
        print("REHABILITATION PROTOCOL")
        print("="*70)
        print(result['protocol'])

        print("\n" + "="*70)
        print("✅ Protocol generation complete!")
        print("="*70)


if __name__ == "__main__":
    main()
