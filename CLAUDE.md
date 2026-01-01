# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize RAG documents (run once before first use)
python init_rag_docs.py

# Run code review (staged + unstaged changes by default)
python main.py
```

Output is written to `code_review_report.md`.

### Git Diff Modes

```python
from git_analyzer import GitManager, DiffMode

GitManager()                                              # ALL (default): staged + unstaged
GitManager(diff_mode=DiffMode.STAGED)                     # staged only
GitManager(diff_mode=DiffMode.UNSTAGED)                   # unstaged only
GitManager(diff_mode=DiffMode.BRANCH, base_ref="main")    # branch comparison
```

## Architecture

Multi-agent AI code review system using RAG and local LLMs. Three agents run concurrently via `asyncio.gather()`:
- **Domain Verifier** - Business logic correctness
- **Security Auditor** - Security vulnerabilities
- **Convention Checker** - Code style and patterns

### Data Flow
```
Git diff → GitManager → Full file content + diff context
                              ↓
RAGService (ChromaDB) → Category-filtered document search
                              ↓
ReviewAgent × 3 → Parallel LLM calls → Aggregated markdown report
```

### Key Components

| File | Class | Purpose |
|------|-------|---------|
| `llm_interface.py` | `LLMProvider` | Abstract base class (Strategy Pattern) for LLM swapping |
| `llm_interface.py` | `OllamaClient` | Local LLM implementation using Ollama |
| `rag_engine.py` | `RAGService` | ChromaDB vector search with category filtering |
| `rag_engine.py` | `preprocess_diff_for_query()` | Cleans diff symbols for better RAG search |
| `git_analyzer.py` | `DiffMode` | Enum for diff modes (UNSTAGED, STAGED, ALL, BRANCH, COMMIT) |
| `git_analyzer.py` | `GitManager` | Extracts diff, file content, project structure via `git ls-files` |
| `review_agents.py` | `ReviewAgent` | Combines RAG context + LLM generation |
| `init_rag_docs.py` | - | Seeds RAG with domain/security/convention rules |

### Adding New LLM Providers

Implement `LLMProvider` abstract class:
```python
class NewClient(LLMProvider):
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Implementation
```

### RAG Categories

Documents are filtered by category metadata: `domain`, `security`, `convention`. Add new rules in `init_rag_docs.py`.

## Current Limitations

- No error handling - crashes on Ollama unavailable, non-git directory, encoding errors
- Token limit risk with large files/projects
- No CLI arguments - model name and paths are hardcoded
- Re-running `init_rag_docs.py` causes duplicate ID errors
