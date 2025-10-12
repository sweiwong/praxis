# PRAXIS Setup Guide

## Quick Start (5 minutes)

### 1. Configure API Keys

Edit the `.env` file and add your Anthropic API key:

```bash
# Open .env file
code .env  # or use: nano .env

# Add your API key
ANTHROPIC_API_KEY=your_actual_api_key_here
```

**Get your Anthropic API key:**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy and paste into `.env`

**Optional: Add PubMed API key** (increases rate limits from 3/sec to 10/sec)
1. Go to https://www.ncbi.nlm.nih.gov/account/
2. Register for free account
3. Go to Settings > API Key Management
4. Copy API key and email to `.env`

### 2. Verify Installation

Test PubMed connection:
```bash
source venv/bin/activate
python3 -c "from src.utils.pubmed import test_pubmed_client; test_pubmed_client()"
```

Test Claude connection:
```bash
source venv/bin/activate
python3 -c "from src.utils.claude_client import test_claude_client; test_claude_client()"
```

### 3. Run Test Protocol Generation

Test with command line:
```bash
source venv/bin/activate
python3 src/main.py
```

This will generate a protocol for "ACL reconstruction rehabilitation"

### 4. Launch Streamlit UI

```bash
source venv/bin/activate
streamlit run src/app.py
```

Your browser should open automatically to http://localhost:8501

## Usage

### Web Interface (Streamlit)

1. Launch app: `streamlit run src/app.py`
2. Enter MSK condition in text box
3. Adjust settings in sidebar (optional)
4. Click "Generate Protocol"
5. View results in tabs:
   - Protocol: Complete rehab protocol
   - Analysis: Evidence grading and key findings
   - Sources: PubMed citations

### Python API

```python
from src.main import PraxisMVP

# Initialize
praxis = PraxisMVP()

# Generate protocol
result = praxis.generate_protocol(
    condition="patellar tendinopathy",
    max_articles=15,
    years_back=10
)

# Access results
print(result["protocol"])      # Rehabilitation protocol
print(result["analysis"])      # Research analysis
print(result["pmids"])         # PubMed IDs
print(result["articles"])      # Full article details
```

## Test Conditions

Try these MSK conditions:

**Knee:**
- ACL reconstruction rehabilitation
- Patellar tendinopathy
- Meniscus repair rehabilitation

**Shoulder:**
- Rotator cuff tendinopathy
- Rotator cuff repair rehabilitation
- Shoulder impingement syndrome

**Back:**
- Low back pain
- Lumbar disc herniation

**Foot/Ankle:**
- Plantar fasciitis
- Achilles tendinopathy
- Ankle sprain rehabilitation

**Other:**
- Tennis elbow (lateral epicondylitis)
- Hip femoroacetabular impingement

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Make sure you created `.env` file (copy from `.env.example`)
- Add your actual API key to `.env`
- Don't use quotes around the key

### "No research found"
- Try different search terms
- Use standard medical terminology
- Examples: "ACL reconstruction" not "torn ACL"

### "PubMed fetch error"
- Check internet connection
- Rate limit may be hit (wait 1 minute)
- Consider adding NCBI API key for higher limits

### Slow protocol generation
- This is normal! Expect 30-60 seconds total
- PubMed search: 5-10 seconds
- Claude analysis: 10-30 seconds
- Protocol generation: 15-40 seconds

## Project Structure

```
praxis/
├── src/
│   ├── main.py              # Core orchestration
│   ├── app.py               # Streamlit UI
│   ├── utils/
│   │   ├── pubmed.py        # PubMed API client
│   │   └── claude_client.py # Claude API client
│   ├── agents/              # Future: multi-agent
│   └── prompts/             # Future: prompt library
├── tests/                   # Unit tests
├── data/cache/              # ChromaDB cache (future)
├── venv/                    # Virtual environment
├── .env                     # API keys (DO NOT COMMIT)
├── .env.example             # Template for .env
├── requirements.txt         # Dependencies
└── README.md                # Project documentation
```

## Next Steps

1. **Test with different conditions** - Try 5-10 different MSK conditions
2. **Refine prompts** - Edit `src/utils/claude_client.py` to improve protocol quality
3. **Add evidence grading** - Enhance analysis to better grade evidence levels
4. **Export protocols** - Add PDF export functionality
5. **Multi-agent architecture** - Implement LangGraph for specialized agents

## Tips

- Start with well-studied conditions (ACL, rotator cuff, low back pain)
- Compare PRAXIS output with actual clinical guidelines
- Adjust search parameters (max_articles, years_back) for different conditions
- Use sidebar in Streamlit for quick condition selection
- Download protocols as markdown for clinical use

## Resources

- PubMed: https://pubmed.ncbi.nlm.nih.gov/
- Anthropic Docs: https://docs.anthropic.com/
- Streamlit Docs: https://docs.streamlit.io/
- PRAXIS GitHub: https://github.com/sweiwong/praxis

## Support

Having issues? Check:
1. `.env` file has correct API key
2. Virtual environment is activated
3. All dependencies installed
4. Internet connection working
5. API keys are valid (not expired)

For more help, open an issue on GitHub!
