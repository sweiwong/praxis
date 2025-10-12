"""
PubMed API client for PRAXIS.

Uses NCBI E-utilities to search medical literature and fetch article details.
Optimized for musculoskeletal rehabilitation research.

API Documentation: https://www.ncbi.nlm.nih.gov/books/NBK25501/
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from datetime import datetime
import os
import time


class PubMedClient:
    """
    Wrapper for PubMed E-utilities API focused on MSK rehabilitation research.

    Key Methods:
    - search_msk_literature(): Search PubMed for MSK research
    - fetch_article_details(): Get full article metadata (title, abstract, authors, etc.)
    """

    def __init__(self):
        # Base URL for PubMed E-utilities
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

        # Get API key from environment (increases rate limits from 3/sec to 10/sec)
        # Only use if it's a real key (not placeholder)
        api_key_raw = os.getenv("NCBI_API_KEY")
        self.api_key = api_key_raw if api_key_raw and not api_key_raw.startswith("your_") else None

        # Email required by NCBI to contact you if issues arise
        # Only use if it's a real email (not placeholder)
        email_raw = os.getenv("NCBI_EMAIL", "")
        self.email = email_raw if email_raw and not email_raw.startswith("your_") else None

        # Rate limiting: 3 requests/sec without key, 10 requests/sec with key
        self.rate_limit = 0.35 if not self.api_key else 0.11  # seconds between requests
        self.last_request_time = 0

    def _rate_limit_wait(self):
        """Enforce rate limiting to respect NCBI guidelines."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def search_msk_literature(
        self,
        condition: str,
        max_results: int = 20,
        years_back: int = 10
    ) -> List[str]:
        """
        Search PubMed for MSK rehabilitation literature.

        Args:
            condition: MSK condition (e.g., "ACL reconstruction", "rotator cuff")
            max_results: Maximum number of papers to retrieve (default: 20)
            years_back: How many years back to search (default: 10)

        Returns:
            List of PubMed IDs (PMIDs) as strings

        Example:
            >>> client = PubMedClient()
            >>> pmids = client.search_msk_literature("ACL reconstruction", max_results=10)
            >>> print(f"Found {len(pmids)} articles")
        """
        # Calculate date range for recent research
        current_year = datetime.now().year
        min_year = current_year - years_back

        # Build MSK-specific search query
        # Focus on: rehabilitation, physical therapy, exercise therapy, protocols
        query = f'({condition}) AND (rehabilitation[Title/Abstract] OR "physical therapy"[Title/Abstract] OR "exercise therapy"[Title/Abstract] OR protocol[Title/Abstract] OR treatment[Title/Abstract])'

        # Add publication type filters for high-quality evidence:
        # - systematic[sb] = systematic reviews
        # - randomized controlled trial[pt] = RCTs
        # - clinical trial[pt] = clinical trials
        query += ' AND (systematic[sb] OR randomized controlled trial[pt] OR clinical trial[pt])'

        # Add date filter (last 10 years by default)
        query += f' AND {min_year}:{current_year}[pdat]'

        print(f"📝 Search query: {query}")

        # Build request parameters
        params = {
            "db": "pubmed",              # Database to search
            "term": query,                # Search query
            "retmax": max_results,        # Maximum results to return
            "retmode": "json",            # Return format (JSON for easy parsing)
            "sort": "relevance",          # Sort by relevance (could also use "pub_date")
        }

        # Add email if available (recommended by NCBI)
        if self.email:
            params["email"] = self.email

        # Add API key if available (increases rate limits)
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            # Enforce rate limiting
            self._rate_limit_wait()

            # Make request to esearch endpoint
            response = requests.get(
                f"{self.base_url}/esearch.fcgi",
                params=params,
                timeout=10
            )

            # Raise exception for bad status codes (4xx, 5xx)
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Extract PubMed IDs from search results
            # Response structure: {"esearchresult": {"idlist": ["12345", "67890", ...]}}
            pmids = data.get("esearchresult", {}).get("idlist", [])

            print(f"✓ Found {len(pmids)} articles")

            return pmids

        except requests.RequestException as e:
            # Log error and return empty list
            print(f"❌ PubMed search error: {e}")
            return []

    def fetch_article_details(self, pmids: List[str]) -> List[Dict]:
        """
        Fetch full details for list of PubMed IDs.

        Args:
            pmids: List of PubMed IDs (strings)

        Returns:
            List of article dictionaries with:
            - pmid: PubMed ID
            - title: Article title
            - abstract: Full abstract text
            - authors: List of author names
            - journal: Journal name
            - year: Publication year
            - doi: DOI identifier (if available)

        Example:
            >>> client = PubMedClient()
            >>> articles = client.fetch_article_details(["38123456", "38123457"])
            >>> for article in articles:
            >>>     print(f"{article['title']} ({article['year']})")
        """
        # Handle empty input
        if not pmids:
            return []

        # Convert list to comma-separated string
        id_string = ",".join(pmids)

        # Build request parameters
        params = {
            "db": "pubmed",              # Database
            "id": id_string,              # Comma-separated PMIDs
            "retmode": "xml",             # XML format contains full article details
        }

        # Add email if available (recommended by NCBI)
        if self.email:
            params["email"] = self.email

        # Add API key if available
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            # Enforce rate limiting
            self._rate_limit_wait()

            # Make request to efetch endpoint
            print(f"📄 Fetching details for {len(pmids)} articles...")
            response = requests.get(
                f"{self.base_url}/efetch.fcgi",
                params=params,
                timeout=30
            )

            # Raise exception for bad status codes
            response.raise_for_status()

            # Parse XML response
            articles = self._parse_pubmed_xml(response.text)

            print(f"✓ Successfully parsed {len(articles)} articles")

            return articles

        except requests.RequestException as e:
            # Log error and return empty list
            print(f"❌ PubMed fetch error: {e}")
            return []

    def _parse_pubmed_xml(self, xml_text: str) -> List[Dict]:
        """
        Parse PubMed XML response into structured article data.

        PubMed XML structure (simplified):
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>12345</PMID>
                    <Article>
                        <ArticleTitle>Title here</ArticleTitle>
                        <Abstract>
                            <AbstractText>Abstract text here</AbstractText>
                        </Abstract>
                        <AuthorList>
                            <Author>
                                <LastName>Smith</LastName>
                                <ForeName>John</ForeName>
                            </Author>
                        </AuthorList>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>

        Args:
            xml_text: Raw XML response from PubMed

        Returns:
            List of article dictionaries
        """
        articles = []

        try:
            # Parse XML string into ElementTree
            root = ET.fromstring(xml_text)

            # Iterate through each PubmedArticle element
            for pub_article in root.findall(".//PubmedArticle"):
                try:
                    # Extract PMID
                    pmid_elem = pub_article.find(".//PMID")
                    pmid = pmid_elem.text if pmid_elem is not None else "Unknown"

                    # Extract article title
                    title_elem = pub_article.find(".//ArticleTitle")
                    title = title_elem.text if title_elem is not None else "No title available"

                    # Extract abstract (may have multiple AbstractText elements)
                    abstract_parts = []
                    for abstract_text in pub_article.findall(".//AbstractText"):
                        # Some abstracts have labels (Background, Methods, Results, Conclusions)
                        label = abstract_text.get("Label", "")
                        text = abstract_text.text if abstract_text.text else ""

                        if label:
                            abstract_parts.append(f"{label}: {text}")
                        else:
                            abstract_parts.append(text)

                    abstract = " ".join(abstract_parts) if abstract_parts else "No abstract available"

                    # Extract authors
                    authors = []
                    for author in pub_article.findall(".//Author"):
                        lastname_elem = author.find("LastName")
                        forename_elem = author.find("ForeName")

                        if lastname_elem is not None and forename_elem is not None:
                            authors.append(f"{forename_elem.text} {lastname_elem.text}")
                        elif lastname_elem is not None:
                            authors.append(lastname_elem.text)

                    # Extract journal name
                    journal_elem = pub_article.find(".//Journal/Title")
                    journal = journal_elem.text if journal_elem is not None else "Unknown journal"

                    # Extract publication year
                    year_elem = pub_article.find(".//PubDate/Year")
                    year = year_elem.text if year_elem is not None else "Unknown year"

                    # Extract DOI (if available)
                    doi = None
                    for article_id in pub_article.findall(".//ArticleId"):
                        if article_id.get("IdType") == "doi":
                            doi = article_id.text
                            break

                    # Create article dictionary
                    article = {
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract,
                        "authors": authors,
                        "journal": journal,
                        "year": year,
                        "doi": doi,
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    }

                    articles.append(article)

                except Exception as e:
                    # Skip this article if parsing fails
                    print(f"⚠️  Warning: Failed to parse article: {e}")
                    continue

        except ET.ParseError as e:
            # Handle XML parsing errors
            print(f"❌ XML parsing error: {e}")
            return []

        return articles


# =============================================================================
# TEST FUNCTION
# =============================================================================

def test_pubmed_client():
    """
    Test function to verify PubMed API connection and parsing.

    Usage:
        python3 -c "from src.utils.pubmed import test_pubmed_client; test_pubmed_client()"
    """
    from dotenv import load_dotenv
    load_dotenv()

    # Create client instance
    client = PubMedClient()

    print("\n" + "="*60)
    print("TESTING PUBMED CLIENT")
    print("="*60)

    # Test 1: Search for ACL rehabilitation
    print("\n[TEST 1] Searching for ACL rehabilitation research...")
    pmids = client.search_msk_literature("ACL reconstruction", max_results=5)

    if pmids:
        print(f"✓ Search successful! Found {len(pmids)} articles")
        print(f"  PMIDs: {', '.join(pmids)}")
    else:
        print("❌ Search failed - no results")
        return

    # Test 2: Fetch article details
    print("\n[TEST 2] Fetching article details...")
    articles = client.fetch_article_details(pmids[:3])  # Get details for first 3

    if articles:
        print(f"✓ Fetch successful! Retrieved {len(articles)} article details\n")

        # Display first article details
        for i, article in enumerate(articles, 1):
            print(f"\n--- Article {i} ---")
            print(f"PMID: {article['pmid']}")
            print(f"Title: {article['title']}")
            print(f"Authors: {', '.join(article['authors'][:3])}{'...' if len(article['authors']) > 3 else ''}")
            print(f"Journal: {article['journal']} ({article['year']})")
            print(f"Abstract: {article['abstract'][:200]}...")
            print(f"URL: {article['url']}")
    else:
        print("❌ Fetch failed - no article details retrieved")

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    test_pubmed_client()
