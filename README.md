# Hybrid AI Code Reviewer

RAG + Multi-Agent 기반 AI 코드 리뷰 시스템

## 개요

Git 변경사항을 분석하여 3가지 관점에서 동시에 코드 리뷰를 수행합니다:

| 에이전트 | 역할 |
|----------|------|
| **Domain Verifier** | 비즈니스 로직 정합성 검증 |
| **Security Auditor** | 보안 취약점 탐지 |
| **Convention Checker** | 코드 스타일/컨벤션 검사 |

## 요구사항

- Python 3.11+
- [Ollama](https://ollama.ai/) (로컬 LLM 실행)
- Git

## 설치

```bash
# 의존성 설치
pip install -r requirements.txt

# Ollama 모델 다운로드
ollama pull qwen2.5-coder:14b
```

## 사용법

```bash
# 1. RAG 문서 초기화 (최초 1회)
python init_rag_docs.py

# 2. 코드 변경 후 리뷰 실행
python main.py
```

결과는 `code_review_report.md`에 저장됩니다.

## 아키텍처

```
Git diff → GitManager → 파일 내용 + diff 컨텍스트
                              ↓
              RAGService → 카테고리별 관련 규칙 검색
                              ↓
              ReviewAgent × 3 → 병렬 LLM 호출
                              ↓
                     code_review_report.md
```

### 주요 컴포넌트

| 파일 | 역할 |
|------|------|
| `main.py` | 진입점, 에이전트 오케스트레이션 |
| `llm_interface.py` | LLM 추상화 (Strategy Pattern) |
| `rag_engine.py` | ChromaDB 기반 RAG 서비스 |
| `git_analyzer.py` | Git diff 추출 및 프로젝트 구조 분석 |
| `review_agents.py` | 코드 리뷰 에이전트 |
| `init_rag_docs.py` | RAG 규칙 문서 초기화 |

## 설정

### Git Diff 모드

```python
from git_analyzer import GitManager, DiffMode

# staged + unstaged (기본값)
git = GitManager()

# staged만
git = GitManager(diff_mode=DiffMode.STAGED)

# 브랜치 비교
git = GitManager(diff_mode=DiffMode.BRANCH, base_ref="main", target_ref="HEAD")
```

### LLM 모델 변경

`main.py`에서 모델명 수정:

```python
llm = OllamaClient(model_name="qwen2.5-coder:14b")
```

### RAG 규칙 추가

`init_rag_docs.py`에서 도메인/보안/컨벤션 규칙 추가 후 재실행.

## 지원 언어

- Java, Kotlin (Spring 프로젝트)
- Python
- JavaScript, TypeScript

## 참고 문서

- [API Reference](API.md) - 클래스/함수 상세 설명
- [CLAUDE.md](CLAUDE.md) - Claude Code 가이드
