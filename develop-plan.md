# 📅 개발 계획서: Hybrid AI Code Reviewer

### 1. 아키텍처 개요
*   **디자인 패턴:** Strategy Pattern (LLM 교체 용이성), Async/Await (병렬 처리)
*   **데이터 파이프라인:**
    1.  `Git Diff` 추출 & 파싱
    2.  변경된 파일의 **전체 코드(Context)** 로딩
    3.  **RAG 엔진:** 변경점과 관련된 도메인/보안/컨벤션 문서 검색 (ChromaDB)
    4.  **Multi-Agent:** 3개의 에이전트가 각기 다른 모델과 프롬프트로 동시 검증
    5.  결과 Aggregation 및 리포트 생성

### 2. 기술 스택
*   **언어:** Python 3.11+
*   **LLM Interface:**
    *   **High-Intelligence:** OpenAI API (GPT-4o/5) or Google Gemini Pro (도메인 검증용)
    *   **Cost-Effective:** Google Gemini 1.5 Flash or Ollama (Local) (컨벤션/보안용)
*   **Vector DB:** **ChromaDB** (로컬 파일 기반, 서버 불필요, 가벼움)
*   **Git Tool:** Python `subprocess` or `gitpython`

---

# 💻 Python 프로토타입 코드

프로젝트 구조를 모듈화하여 작성했습니다. 파일별로 복사하여 테스트해 보실 수 있습니다.

### 1. `llm_interface.py` (모델 추상화)
모델이 바뀌어도 비즈니스 로직은 건드리지 않도록 추상 클래스를 정의합니다.

```python
from abc import ABC, abstractmethod
import os

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """비동기로 답변 생성"""
        pass

# [구현체 1] OpenAI (GPT-4o, GPT-5 등 - 도메인 검증용)
class OpenAIClient(LLMProvider):
    def __init__(self, model_name="gpt-4o"):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content

# [구현체 2] Gemini (Flash - 가성비/속도용) 또는 Local LLM
class GeminiClient(LLMProvider):
    def __init__(self, model_name="gemini-1.5-flash"):
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model_name)

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Gemini는 System Prompt를 생성 시점에 설정하거나 프롬프트에 합칩니다.
        full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
        response = await self.model.generate_content_async(full_prompt)
        return response.text

# [구현체 3] Ollama (완전 로컬 - 보안용)
class OllamaClient(LLMProvider):
    def __init__(self, model_name="qwen2.5-coder:14b"):
        import ollama
        self.model_name = model_name
        # Ollama의 비동기 클라이언트는 라이브러리 버전에 따라 다르므로 AsyncClient 사용 권장
        from ollama import AsyncClient
        self.client = AsyncClient()

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat(model=self.model_name, messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ])
        return response['message']['content']
```

### 2. `rag_engine.py` (가벼운 RAG)
문서 전체를 LLM에 넣지 않고, 관련된 부분만 검색하여 토큰을 절약합니다.

```python
import chromadb

class RAGService:
    def __init__(self, db_path="./chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        # 컬렉션을 도메인/보안/컨벤션으로 분리하거나 메타데이터로 구분
        self.collection = self.client.get_or_create_collection(name="code_docs")

    def add_documents(self, docs: list[str], metadatas: list[dict], ids: list[str]):
        """문서 벡터화 및 저장 (최초 1회 실행용)"""
        self.collection.add(documents=docs, metadatas=metadatas, ids=ids)

    def search(self, query_text: str, category: str, k=3) -> str:
        """
        category: 'domain', 'security', 'convention'
        git diff 내용을 쿼리로 관련 문서를 검색
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=k,
            where={"category": category} # 카테고리 필터링
        )
        
        if not results['documents'][0]:
            return "관련된 문서가 없습니다."
        
        # 검색된 문서 내용을 하나의 문자열로 합침
        return "\n\n".join(results['documents'][0])
```

### 3. `git_analyzer.py` (Git 처리)
Diff뿐만 아니라 "파일 전체 내용"을 같이 읽어옵니다 (할루시네이션 방지).

```python
import subprocess
import os

class GitManager:
    def get_diff_files(self):
        # 변경된 파일 목록 추출
        result = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
        return [f for f in result.stdout.split('\n') if f and f.endswith(('.java', '.py', '.kt'))] # 소스코드만 필터링

    def get_file_content(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def get_diff_context(self, file_path):
        # 특정 파일의 Diff 내용만 추출
        result = subprocess.run(["git", "diff", file_path], capture_output=True, text=True)
        return result.stdout
```

### 4. `review_agents.py` (멀티 에이전트 로직)
각 에이전트가 `LLMProvider`를 주입받아 동작합니다.

```python
class ReviewAgent:
    def __init__(self, name: str, llm: LLMProvider, rag: RAGService, category: str):
        self.name = name
        self.llm = llm
        self.rag = rag
        self.category = category

    async def review(self, file_path: str, code_content: str, diff_content: str) -> str:
        # 1. RAG: 변경된 코드(diff)와 관련된 문서 검색
        # 토큰 절약을 위해 diff 내용 중 일부 키워드만 쿼리로 쓰거나 diff 전체를 씀
        relevant_docs = self.rag.search(query_text=diff_content[:1000], category=self.category, k=3)

        # 2. 프롬프트 구성
        system_prompt = f"""
        당신은 {self.name} 전문가입니다.
        아래 제공되는 [참고 문서]를 엄격히 준수하여 코드를 리뷰하세요.
        
        [참고 문서]
        {relevant_docs}
        """

        user_prompt = f"""
        [대상 파일] {file_path}
        [전체 코드]
        {code_content}
        
        [변경 사항 (Git Diff)]
        {diff_content}
        
        위 변경 사항에 대해 {self.category} 관점에서 문제점을 지적하세요.
        문제가 없다면 'PASS'라고만 답하세요.
        """

        # 3. LLM 호출
        print(f"🚀 [{self.name}] 검증 시작: {file_path}")
        result = await self.llm.generate(system_prompt, user_prompt)
        return f"## 🕵️ {self.name} Review\n{result}\n"
```

### 5. `main.py` (오케스트레이션)
여기서 **고성능 모델**과 **경량 모델**을 에이전트별로 할당하고 **동시에 실행**합니다.

```python
import asyncio
from llm_interface import OpenAIClient, GeminiClient, OllamaClient
from rag_engine import RAGService
from git_analyzer import GitManager
from review_agents import ReviewAgent

async def main():
    # 1. 인프라 설정
    rag = RAGService()
    git = GitManager()
    
    # 2. 모델 할당 (전략적 배치)
    # 도메인 검증 -> 가장 똑똑한 모델 (GPT-4o or GPT-5)
    smart_llm = OpenAIClient(model_name="gpt-4o") 
    
    # 컨벤션/시큐어코딩 -> 빠르고 컨텍스트 넓은 가성비 모델 (Gemini Flash or Ollama)
    fast_llm = GeminiClient(model_name="gemini-1.5-flash")
    # fast_llm = OllamaClient(model_name="qwen2.5-coder:14b") # 로컬 원할 경우 교체 가능

    # 3. 에이전트 초기화
    agents = [
        ReviewAgent("Domain Verifier", smart_llm, rag, category="domain"),
        ReviewAgent("Security Auditor", fast_llm, rag, category="security"),
        ReviewAgent("Convention Checker", fast_llm, rag, category="convention"),
    ]

    # 4. 변경된 파일 분석 시작
    changed_files = git.get_diff_files()
    if not changed_files:
        print("변경 사항이 없습니다.")
        return

    full_report = []

    for file_path in changed_files:
        print(f"\n📂 Analyzing: {file_path} ...")
        
        code_content = git.get_file_content(file_path)
        diff_content = git.get_diff_context(file_path)

        # 5. 비동기 병렬 실행 (Asyncio Gather)
        # 3명의 에이전트가 동시에 질문을 던짐 -> 시간 단축
        tasks = [agent.review(file_path, code_content, diff_content) for agent in agents]
        results = await asyncio.gather(*tasks)
        
        full_report.append(f"# File: {file_path}\n" + "\n".join(results))

    # 6. 최종 리포트 출력
    with open("code_review_report.md", "w") as f:
        f.write("\n\n".join(full_report))
    print("\n✅ 리뷰 완료! 'code_review_report.md'를 확인하세요.")

if __name__ == "__main__":
    # 문서 임베딩 예시 (최초 1회만 필요, 실제로는 별도 스크립트로 분리)
    # rag = RAGService()
    # rag.add_documents(
    #     docs=["주문 취소 시 포인트는 즉시 환불되어야 한다...", "SQL Injection 방지를 위해 PreparedStatement 사용..."],
    #     metadatas=[{"category": "domain"}, {"category": "security"}],
    #     ids=["rule_1", "rule_2"]
    # )
    
    asyncio.run(main())
```

---

### 핵심 포인트 요약

1.  **추상화 (`LLMProvider`)**: `OpenAIClient`, `GeminiClient`, `OllamaClient`를 언제든 갈아끼울 수 있습니다. 나중에 회사 정책이 바뀌어도 코드 수정은 최소화됩니다.
2.  **RAG 적용 (`search`)**: 모든 문서를 프롬프트에 넣지 않습니다. `category="domain"` 식으로 필터링하고, `k=3`개만 가져와서 **토큰 소비를 최소화**했습니다.
3.  **병렬 처리 (`asyncio.gather`)**: 도메인, 보안, 컨벤션 검사가 순차적이 아니라 **동시에** 진행됩니다. API 응답 대기 시간을 획기적으로 줄입니다.
4.  **하이브리드 전략**:
    *   **도메인 에이전트**에는 `smart_llm` (GPT-4o)을 주입.
    *   **컨벤션/보안 에이전트**에는 `fast_llm` (Gemini Flash/Local)을 주입.
5.  **맥락 보존**: `git_analyzer`에서 `diff`만 가져오는 게 아니라 `get_file_content`로 **파일 전체**를 가져와서 할루시네이션을 방지했습니다.