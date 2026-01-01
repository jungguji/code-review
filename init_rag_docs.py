"""RAG 테스트용 샘플 문서 초기화 스크립트"""

from rag_engine import RAGService


def init_sample_documents():
    rag = RAGService()

    # 도메인 규칙 문서
    domain_docs = [
        "주문 취소 시 포인트는 즉시 환불되어야 한다. 환불 처리는 반드시 트랜잭션 내에서 수행되어야 하며, 부분 취소 시에도 포인트 비율 계산이 정확해야 한다.",
        "사용자 인증 토큰은 24시간 후 만료되어야 한다. 리프레시 토큰은 7일간 유효하며, 로그아웃 시 모든 토큰을 무효화해야 한다.",
        "결제 금액 계산 시 부동소수점 연산을 피하고 정수(원 단위) 또는 Decimal 타입을 사용해야 한다. 할인율 적용 시 반올림 정책을 명확히 해야 한다.",
        "재고 차감은 결제 완료 후에만 수행되어야 하며, 동시성 문제를 방지하기 위해 비관적 락(Pessimistic Lock)을 사용해야 한다.",
    ]

    # 보안 규칙 문서
    security_docs = [
        "SQL Injection 방지를 위해 반드시 PreparedStatement 또는 ORM의 파라미터 바인딩을 사용해야 한다. 문자열 연결로 쿼리를 생성하지 말 것.",
        "사용자 입력값은 반드시 검증(Validation)과 이스케이프(Escape) 처리를 해야 한다. XSS 공격 방지를 위해 HTML 출력 시 인코딩 필수.",
        "비밀번호는 평문 저장 금지. bcrypt, scrypt, argon2 등의 안전한 해싱 알고리즘을 사용해야 한다. 솔트(salt)는 자동 생성되는 것을 사용할 것.",
        "API 엔드포인트는 인증(Authentication)과 인가(Authorization) 검증을 필수로 해야 한다. 민감한 데이터 접근 시 추가 권한 검증 필요.",
        "로그에 비밀번호, API 키, 개인정보(주민번호, 카드번호 등)를 출력하지 말 것. 마스킹 처리 필수.",
    ]

    # 컨벤션 규칙 문서
    convention_docs = [
        "함수명은 동사로 시작해야 한다 (예: get_user, create_order, validate_input). 클래스명은 명사형 PascalCase를 사용한다.",
        "한 함수는 하나의 역할만 수행해야 한다 (Single Responsibility). 함수 길이는 30줄 이내를 권장하며, 50줄을 초과하면 분리를 검토한다.",
        "매직 넘버 사용 금지. 상수로 정의하고 의미 있는 이름을 부여해야 한다 (예: MAX_RETRY_COUNT = 3).",
        "예외 처리 시 빈 catch 블록 금지. 최소한 로깅을 수행하거나, 예외를 상위로 전파해야 한다.",
        "코드 중복(DRY 원칙 위반)을 피해야 한다. 3번 이상 반복되는 로직은 함수로 추출한다.",
    ]

    # 문서 추가
    all_docs = []
    all_metadatas = []
    all_ids = []

    for i, doc in enumerate(domain_docs):
        all_docs.append(doc)
        all_metadatas.append({"category": "domain"})
        all_ids.append(f"domain_{i+1}")

    for i, doc in enumerate(security_docs):
        all_docs.append(doc)
        all_metadatas.append({"category": "security"})
        all_ids.append(f"security_{i+1}")

    for i, doc in enumerate(convention_docs):
        all_docs.append(doc)
        all_metadatas.append({"category": "convention"})
        all_ids.append(f"convention_{i+1}")

    rag.add_documents(docs=all_docs, metadatas=all_metadatas, ids=all_ids)

    print(f"✅ RAG 문서 초기화 완료!")
    print(f"   - Domain 규칙: {len(domain_docs)}개")
    print(f"   - Security 규칙: {len(security_docs)}개")
    print(f"   - Convention 규칙: {len(convention_docs)}개")
    print(f"   - 총 {len(all_docs)}개 문서 저장됨")


if __name__ == "__main__":
    init_sample_documents()
