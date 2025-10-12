"""
Claude API client for PRAXIS.

Handles all interactions with Anthropic's Claude API for:
- Research analysis and synthesis
- Evidence grading
- Protocol generation
- Patient education materials

Uses Claude Sonnet for medical reasoning tasks.
"""

import anthropic
import os
from typing import Optional, Dict


class ClaudeClient:
    """
    Wrapper for Claude API optimized for MSK rehabilitation research.

    Key Methods:
    - analyze_research(): Analyze research papers and grade evidence
    - generate_protocol(): Create phase-based rehabilitation protocol
    - generate_education(): Create patient education handout (future)
    """

    def __init__(self):
        # Initialize Anthropic client with API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment. "
                "Please set it in your .env file."
            )

        self.client = anthropic.Anthropic(api_key=api_key)

        # Model selection: Claude Sonnet for medical reasoning
        # Sonnet provides excellent balance of speed, cost, and accuracy
        self.model = "claude-sonnet-4-20250514"

        # Maximum tokens for responses (adjust based on protocol length)
        self.max_tokens = 4096

    def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3
    ) -> str:
        """
        Generate Claude response with custom system prompt.

        Args:
            system_prompt: System instructions defining Claude's role and behavior
            user_message: User query or content to analyze
            temperature: Sampling temperature (0.0-1.0)
                        Lower = more focused/deterministic
                        Higher = more creative/variable
                        For medical content, use 0.2-0.3

        Returns:
            Claude's text response

        Raises:
            anthropic.APIError: If API request fails
        """
        try:
            # Create message with Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=temperature,      # Lower temp for medical accuracy
                system=system_prompt,          # System instructions
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            # Extract text from response
            # Claude returns a list of content blocks; we want the text from the first one
            response_text = message.content[0].text

            return response_text

        except anthropic.APIError as e:
            # Handle API errors (rate limits, authentication, etc.)
            error_msg = f"Claude API error: {str(e)}"
            print(f"❌ {error_msg}")
            return f"Error generating response: {str(e)}"

    def analyze_research(
        self,
        articles: list,
        condition: str
    ) -> str:
        """
        Analyze research papers for MSK condition and grade evidence.

        Takes list of research articles and synthesizes key findings,
        grades evidence quality, and identifies consensus.

        Args:
            articles: List of article dictionaries from PubMed
                     Each dict should have: title, abstract, authors, journal, year
            condition: MSK condition being researched

        Returns:
            Structured analysis with evidence grades and key findings

        Example:
            >>> client = ClaudeClient()
            >>> analysis = client.analyze_research(articles, "ACL reconstruction")
            >>> print(analysis)
        """
        # System prompt for research analysis
        # This defines Claude's role as an expert PT and research analyst
        system_prompt = """You are an expert physical therapist and research analyst
specializing in musculoskeletal rehabilitation. Your role is to analyze research
literature and extract clinically actionable insights for rehabilitation protocols.

Your analysis should:
1. Grade evidence quality using this hierarchy:
   - 1A: Systematic review of RCTs
   - 1B: High-quality RCT
   - 2A: High-quality cohort study
   - 2B: Case-control study
   - 3: Expert opinion/consensus statement
   - 4: Anecdotal evidence

2. Identify consensus across studies (what do most high-quality studies agree on?)

3. Extract practical rehabilitation insights:
   - Exercise progressions with dosage parameters (sets, reps, load, frequency)
   - Return-to-sport or return-to-function criteria
   - Contraindications and precautions
   - Expected recovery timelines

4. Flag any conflicting findings or research gaps

Focus on actionable clinical insights, not just research summaries."""

        # Format articles into readable text for Claude
        research_content = self._format_articles_for_analysis(articles, condition)

        # User message with research content
        user_message = f"""Analyze the following research on {condition}.

{research_content}

Provide a structured analysis with:

1. **Evidence Summary**: What does the research consensus say about rehabilitation for {condition}?

2. **Key Interventions** (with evidence grades):
   - List main rehabilitation interventions
   - Grade each one (1A, 1B, 2A, etc.)
   - Include dosage parameters where available

3. **Progression Guidelines**: How should rehabilitation progress over time?

4. **Return-to-Activity Criteria**: What criteria indicate readiness to progress or return to sport?

5. **Contraindications/Precautions**: What should clinicians avoid or watch for?

6. **Recovery Timeline**: Expected timeframes for rehabilitation phases

7. **Research Gaps**: Any conflicting findings or areas needing more research?"""

        # Generate analysis
        print("🤖 Analyzing research with Claude...")
        analysis = self.generate_response(system_prompt, user_message, temperature=0.3)

        return analysis

    def generate_protocol(
        self,
        analysis: str,
        condition: str
    ) -> str:
        """
        Generate phase-based rehabilitation protocol from research analysis.

        Takes synthesized research analysis and creates a structured,
        clinician-ready rehabilitation protocol.

        Args:
            analysis: Research analysis output from analyze_research()
            condition: MSK condition

        Returns:
            Formatted rehabilitation protocol with phases, exercises, and criteria

        Example:
            >>> protocol = client.generate_protocol(analysis, "ACL reconstruction")
            >>> print(protocol)
        """
        # System prompt for protocol generation
        system_prompt = """You are an expert physical therapist creating evidence-based
rehabilitation protocols for musculoskeletal conditions.

Your protocols should be:
1. **Phase-based**: Typically 3-4 phases with clear timeframes
2. **Specific**: Include exact exercises with sets, reps, load, frequency
3. **Evidence-graded**: Cite evidence levels for each intervention (1A, 1B, 2A, etc.)
4. **Progressive**: Clear criteria for advancing between phases
5. **Clinician-ready**: Can be implemented immediately by a PT or AT

Format each phase with:
- Phase name and timeframe (e.g., "Phase 1: Pain Management (Weeks 1-2)")
- Goals for the phase
- Exercises with dosage:
  * Exercise name
  * Sets x Reps at Load
  * Frequency (times per day/week)
  * Evidence grade
- Progression criteria (when to advance to next phase)

Include:
- Contraindications and red flags
- Outcome measures to track progress
- Return-to-activity criteria (if applicable)

Use clear, professional language that practicing clinicians would use."""

        # User message with analysis
        user_message = f"""Based on this research analysis for {condition},
generate a complete, evidence-based rehabilitation protocol.

Research Analysis:
{analysis}

Create a protocol with the following structure:

# PRAXIS PROTOCOL: {condition}

## CONDITION OVERVIEW
[Brief description of condition, typical presentation, common patient populations]

## ASSESSMENT
[Key assessment tools, tests, differential diagnoses]

## REHABILITATION PROTOCOL

### Phase 1: [Phase Name] (Timeframe)
**Goals**: [Phase objectives]

**Interventions**:
- [Exercise/intervention name] (Evidence Grade: [1A/1B/etc])
  - Dosage: [sets] x [reps] at [load], [frequency]
  - Rationale: [Brief clinical reasoning]

**Progression Criteria**:
- [Criteria for advancing to Phase 2]

### Phase 2: [Phase Name] (Timeframe)
[Same structure as Phase 1]

### Phase 3: [Phase Name] (Timeframe)
[Same structure as Phase 1]

### Phase 4: [Return to Sport/Activity] (Timeframe)
[Same structure as Phase 1]

## CONTRAINDICATIONS & RED FLAGS
- [List conditions requiring referral or caution]

## OUTCOME MEASURES
- [Standardized assessments to track progress]

## EVIDENCE BASE
- [Summary of research quality and sources]

Generate a complete, practical protocol now."""

        # Generate protocol with lower temperature for consistency
        print("📋 Generating rehabilitation protocol...")
        protocol = self.generate_response(system_prompt, user_message, temperature=0.2)

        return protocol

    def _format_articles_for_analysis(
        self,
        articles: list,
        condition: str
    ) -> str:
        """
        Format article list into readable text for Claude analysis.

        Args:
            articles: List of article dictionaries
            condition: MSK condition

        Returns:
            Formatted string with article details
        """
        if not articles:
            return f"No research articles found for {condition}."

        formatted = f"Research Articles on {condition}:\n\n"

        for i, article in enumerate(articles, 1):
            formatted += f"--- Article {i} ---\n"
            formatted += f"Title: {article.get('title', 'Unknown')}\n"
            formatted += f"Authors: {', '.join(article.get('authors', [])[:3])}\n"
            formatted += f"Journal: {article.get('journal', 'Unknown')} ({article.get('year', 'Unknown')})\n"
            formatted += f"PMID: {article.get('pmid', 'Unknown')}\n"
            formatted += f"Abstract: {article.get('abstract', 'No abstract available')}\n"
            formatted += "\n"

        return formatted


# =============================================================================
# TEST FUNCTION
# =============================================================================

def test_claude_client():
    """
    Test function to verify Claude API connection.

    Usage:
        python3 -c "from src.utils.claude_client import test_claude_client; test_claude_client()"
    """
    from dotenv import load_dotenv
    load_dotenv()

    print("\n" + "="*60)
    print("TESTING CLAUDE CLIENT")
    print("="*60)

    try:
        # Create client instance
        client = ClaudeClient()
        print("✓ Claude client initialized successfully")

        # Test simple query
        print("\n[TEST] Asking Claude about ACL rehabilitation principles...")

        system_prompt = "You are an expert physical therapist specializing in MSK rehabilitation."
        user_message = "What are the 3 most important principles for ACL reconstruction rehabilitation? Be concise."

        response = client.generate_response(system_prompt, user_message)

        print("\nClaude's Response:")
        print("-" * 60)
        print(response)
        print("-" * 60)

        print("\n✓ Test successful!")

    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("\nPlease ensure you have:")
        print("1. Created a .env file (copy from .env.example)")
        print("2. Added your ANTHROPIC_API_KEY to .env")
        print("3. Get your API key from: https://console.anthropic.com/")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    test_claude_client()
