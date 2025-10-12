# 🏃 PRAXIS

**Evidence-based musculoskeletal rehabilitation protocols powered by AI**

PRAXIS is an open-source AI research agent that searches medical literature and generates clinician-ready rehabilitation protocols for musculoskeletal conditions. Built for physical therapists, athletic trainers, and movement practitioners.

## The Problem

MSK rehabilitation practitioners need evidence-based treatment protocols but:
- Don't have time to read research papers (2-3 hours per condition)
- Can't translate academic jargon into clinical practice
- Struggle to synthesize conflicting research findings
- Need actionable protocols, not systematic reviews

## The Solution

PRAXIS searches PubMed literature and generates:
- Phase-based rehabilitation protocols
- Exercise progressions with dosage parameters (sets, reps, load, frequency)
- Evidence grading (1A, 1B, 2A, etc.)
- Return-to-sport criteria
- Patient education handouts

**Target output:** Complete MSK rehab protocol in 2 minutes (vs 2-3 hours manual research)

## Features

- 🔍 **Smart Literature Search**: Queries PubMed for RCTs, systematic reviews, and clinical trials
- 🧠 **Evidence Synthesis**: Grades research quality and identifies consensus
- 📋 **Protocol Generation**: Creates phase-based rehab protocols with exercise progressions
- 💪 **Dosage Parameters**: Includes sets, reps, load, and frequency
- 📚 **Source Citations**: All recommendations linked to research with evidence grades

## Tech Stack

- **Python 3.11+**
- **Claude API** (Anthropic) - Medical reasoning and protocol generation
- **PubMed API** - Medical literature search
- **Streamlit** - Web interface

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/sweiwong/praxis.git
cd praxis
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

```bash
cp .env.example .env
# Edit .env with your API keys:
# - ANTHROPIC_API_KEY (required) - Get from https://console.anthropic.com/
# - NCBI_API_KEY (optional) - Get from https://www.ncbi.nlm.nih.gov/account/
```

### 5. Run the App

```bash
streamlit run src/app.py
```

## Usage

### Web Interface

1. Launch Streamlit app: `streamlit run src/app.py`
2. Enter an MSK condition (e.g., "ACL reconstruction rehabilitation")
3. Click "Generate Protocol"
4. View protocol, research analysis, and sources

### Python API

```python
from src.main import PraxisMVP

# Initialize PRAXIS
praxis = PraxisMVP()

# Generate protocol
result = praxis.generate_protocol("patellar tendinopathy")

# Access results
print(result["protocol"])
print(result["analysis"])
print(result["pmids"])
```

## Supported MSK Conditions

- ACL reconstruction rehabilitation
- Rotator cuff tendinopathy/tears
- Patellar tendinopathy
- Low back pain
- Plantar fasciitis
- Tennis elbow (lateral epicondylitis)
- Hip femoroacetabular impingement
- Ankle sprains
- And more...

## Project Structure

```
praxis/
├── src/
│   ├── main.py              # Core orchestration logic
│   ├── app.py               # Streamlit web interface
│   ├── utils/
│   │   ├── pubmed.py        # PubMed API client
│   │   └── claude_client.py # Claude API client
│   ├── prompts/
│   │   └── system_prompts.py # Agent prompts
│   └── agents/              # Future: multi-agent architecture
├── tests/                   # Unit tests
├── data/cache/              # ChromaDB cache (future)
└── requirements.txt         # Python dependencies
```

## Roadmap

### MVP (Current)
- [x] PubMed literature search
- [x] Claude-powered research analysis
- [x] Protocol generation
- [x] Streamlit UI

### v0.2 (Next)
- [ ] XML parsing for full article details
- [ ] Evidence grading system (1A, 1B, 2A, etc.)
- [ ] Patient education handout generation
- [ ] Export protocols (PDF, Markdown)

### v0.3 (Future)
- [ ] Multi-agent architecture with LangGraph
- [ ] ChromaDB caching layer
- [ ] Custom research sources (BJSM, AJSM, JOSPT)
- [ ] User feedback loop for protocol refinement

## Contributing

This is an open-source project! Contributions welcome.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Disclaimer

⚠️ **IMPORTANT**: PRAXIS is a research tool designed to assist clinical judgment. It does not provide medical advice and should not replace professional clinical assessment, diagnosis, or treatment. Always use clinical reasoning and consider individual patient factors.

## License

MIT License - see [LICENSE](LICENSE) file for details

## Author

**Wei Wong**
Head of Product & AI Systems at Phy Health
GitHub: [@sweiwong](https://github.com/sweiwong)

## Acknowledgments

- Built with [Claude](https://www.anthropic.com/claude) by Anthropic
- Medical literature from [PubMed](https://pubmed.ncbi.nlm.nih.gov/)
- Inspired by the need for evidence-based MSK rehabilitation

---

**Built with ❤️ for physical therapists and movement practitioners**
