import asyncio
from llm_interface import OllamaClient
from rag_engine import RAGService
from git_analyzer import GitManager
from review_agents import ReviewAgent


async def main():
    # 1. 인프라 설정
    rag = RAGService()
    git = GitManager()

    # 2. Ollama 클라이언트 초기화
    llm = OllamaClient(model_name="qwen2.5-coder:14b")

    # 3. 에이전트 초기화 (도메인, 보안, 컨벤션)
    agents = [
        ReviewAgent("Domain Verifier", llm, rag, category="domain"),
        ReviewAgent("Security Auditor", llm, rag, category="security"),
        ReviewAgent("Convention Checker", llm, rag, category="convention"),
    ]

    # 4. 변경된 파일 분석 시작
    changed_files = git.get_diff_files()
    if not changed_files:
        print("변경 사항이 없습니다.")
        return

    # 프로젝트 구조 가져오기 (1회만 실행)
    project_structure = git.get_project_structure()

    full_report = []

    for file_path in changed_files:
        print(f"\n📂 Analyzing: {file_path} ...")

        code_content = git.get_file_content(file_path)
        diff_content = git.get_diff_context(file_path)

        # 5. 비동기 병렬 실행 (3명의 에이전트가 동시에 검증)
        tasks = [agent.review(file_path, code_content, diff_content, project_structure) for agent in agents]
        results = await asyncio.gather(*tasks)

        full_report.append(f"# File: {file_path}\n" + "\n".join(results))

    # 6. 최종 리포트 출력
    with open("code_review_report.md", "w", encoding="utf-8") as f:
        f.write("\n\n".join(full_report))
    print("\n✅ 리뷰 완료! 'code_review_report.md'를 확인하세요.")


if __name__ == "__main__":
    asyncio.run(main())
