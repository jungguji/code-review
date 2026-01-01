개선 필요 사항 (심각도 순)

  1. 에러 처리 전무 🔴

  - Ollama 연결 실패, Git 저장소 아님, 파일 인코딩 오류 등 → 모두 크래시
  - 모든 모듈에 try-except 없음

  2. 토큰 한계 초과 가능성 🔴

  - project_structure + code_content + diff_content + relevant_docs
  - 대형 파일/프로젝트에서 14B 모델 컨텍스트 윈도우 초과

  5. 중복 문서 ID 처리 없음 🟡

  - init_rag_docs.py 재실행 시 ID 충돌 에러

  6. 병렬 실행 실효성 🟠

  - 3개 에이전트가 동일 Ollama 인스턴스 호출
  - Ollama 기본 설정상 순차 처리 → 병렬 효과 없음

  7. 타임아웃/재시도 없음 🟠

  - LLM 무한 대기 가능
  - 일시적 오류에 취약

  8. 로깅 부재 🟢

  - print()만 사용
  - 디버깅/모니터링 어려움

  9. CLI 인자 없음 🟢

  - 모델명, 대상 경로 등 하드코딩
  - 유연성 부족