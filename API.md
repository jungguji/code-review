# API Reference

## 파일별 역할

| 파일 | 역할 |
|------|------|
| `main.py` | 진입점 - 에이전트 초기화 및 병렬 실행 오케스트레이션 |
| `llm_interface.py` | LLM 추상화 - Strategy Pattern으로 모델 교체 용이 |
| `rag_engine.py` | RAG 서비스 - ChromaDB 기반 문서 검색 |
| `git_analyzer.py` | Git 분석 - diff 추출 및 프로젝트 구조 파악 |
| `review_agents.py` | 리뷰 에이전트 - RAG + LLM 조합으로 코드 검증 |
| `init_rag_docs.py` | RAG 초기화 - 도메인/보안/컨벤션 규칙 문서 등록 |

---

## llm_interface.py

| 클래스/함수 | 설명 |
|-------------|------|
| `LLMProvider` | LLM 제공자 추상 클래스 (ABC) |
| `LLMProvider.generate()` | 시스템/유저 프롬프트로 비동기 응답 생성 |
| `OllamaClient` | Ollama 로컬 LLM 구현체 |

---

## rag_engine.py

| 클래스/함수 | 설명 |
|-------------|------|
| `preprocess_diff_for_query()` | Git diff에서 메타데이터 제거하고 순수 코드만 추출 |
| `RAGService` | ChromaDB 기반 벡터 검색 서비스 |
| `RAGService.add_documents()` | 문서 벡터화 및 저장 (최초 1회) |
| `RAGService.search()` | 카테고리별 관련 문서 검색 (top-k) |

---

## git_analyzer.py

| 클래스/함수 | 설명 |
|-------------|------|
| `DiffMode` | Git diff 모드 Enum (UNSTAGED, STAGED, ALL, BRANCH, COMMIT) |
| `GitManager` | Git diff 및 파일 분석 관리자 |
| `GitManager._build_diff_command()` | diff 모드에 따른 git 명령어 동적 생성 |
| `GitManager.get_diff_files()` | 변경된 소스코드 파일 목록 반환 |
| `GitManager.get_file_content()` | 파일 전체 내용 로드 |
| `GitManager.get_diff_context()` | 특정 파일의 diff 내용 추출 |
| `GitManager.get_project_structure()` | 프로젝트 디렉토리 트리 문자열 생성 |

---

## review_agents.py

| 클래스/함수 | 설명 |
|-------------|------|
| `ReviewAgent` | 코드 리뷰 에이전트 (RAG + LLM 조합) |
| `ReviewAgent.review()` | 파일에 대한 카테고리별 코드 리뷰 수행 |

---

## 에이전트 카테고리

| 카테고리 | 역할 |
|----------|------|
| `domain` | 비즈니스 로직 정합성 검증 |
| `security` | 보안 취약점 탐지 |
| `convention` | 코드 스타일/컨벤션 검사 |
