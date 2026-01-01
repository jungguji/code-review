import chromadb


def preprocess_diff_for_query(diff_content: str) -> str:
    """
    Git diff에서 의미 있는 코드만 추출하여 RAG 쿼리용으로 정제

    제거 대상:
    - @@ ... @@ 헝크 헤더
    - --- a/file, +++ b/file 파일 헤더
    - diff --git, index 라인

    처리:
    - +, -, 공백 접두사 제거하여 순수 코드만 추출
    """
    lines = diff_content.split('\n')
    cleaned_lines = []

    for line in lines:
        # 메타데이터 라인 스킵
        if line.startswith(('@@', '---', '+++', 'diff --git', 'index ')):
            continue

        # +/- /공백 접두사 제거
        if line.startswith(('+', '-', ' ')):
            cleaned_lines.append(line[1:])

    return '\n'.join(cleaned_lines)


class RAGService:
    """ChromaDB 기반 RAG 서비스 - 관련 문서 검색으로 토큰 절약"""

    def __init__(self, db_path: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="code_docs")

    def add_documents(self, docs: list[str], metadatas: list[dict], ids: list[str]):
        """문서 벡터화 및 저장 (최초 1회 실행용)"""
        self.collection.add(documents=docs, metadatas=metadatas, ids=ids)

    def search(self, query_text: str, category: str, k: int = 3) -> str:
        """
        카테고리별 관련 문서 검색

        Args:
            query_text: 검색 쿼리 (git diff 내용)
            category: 'domain', 'security', 'convention' 중 하나
            k: 검색 결과 개수

        Returns:
            검색된 문서 내용을 합친 문자열
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=k,
            where={"category": category}
        )

        if not results['documents'][0]:
            return "관련된 문서가 없습니다."

        return "\n\n".join(results['documents'][0])
