# Rulebook QnA

> "The Rulebook That Argues With Itself" — An evidence-grounded university regulations Q&A system with three-state reasoning.

## Overview

Rulebook QnA is a Retrieval-Augmented Generation (RAG) system that goes beyond standard Q&A by detecting three distinct states for every question:

| State | Meaning |
|-------|---------|
| **ANSWERABLE** | The corpus contains sufficient evidence to answer |
| **NOT_FOUND** | The corpus does not contain enough information — the system refuses to guess |
| **CONTRADICTORY** | Two or more rules in the corpus conflict — the system shows both sides |

## Status

🚧 Under active development.

## Quick Start

```bash
git clone https://github.com/raj-1807/rulebook-qna.git
cd rulebook-qna
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
uvicorn backend.main:app --reload
```

## License

MIT
