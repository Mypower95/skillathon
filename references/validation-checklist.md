# Validation Checklist

## Skill Files

- `SKILL.md`가 있다.
- `README.md`가 문제, 실행 방법, 결과, 검증, 한계를 설명한다.
- `references/`에 스키마, 디자인, Netlify, Gmail, 검증 기준이 있다.
- `mock-data/`에 공개 가능한 샘플 CSV가 있다.

## Data Safety

- 실제 고객명, 전화번호, 이메일, 주소가 없다.
- API key, token, webhook URL이 없다.
- 내부 전용 URL이나 비공개 매장 코드가 없다.

## Execution

- `scripts/analyze_orders.py`가 mock CSV를 읽고 JSON을 만든다.
- `scripts/anonymize_orders.py`가 보안 컬럼을 더미 값으로 바꾼다.
- `scripts/build_report.py`가 JSON을 읽고 HTML을 만든다.
- HTML을 브라우저에서 열 수 있다.
- Netlify 배포를 실행했거나, 실행하지 못한 이유와 수동 절차를 기록했다.
- Gmail 초안을 생성했거나, 초안 텍스트를 예시로 남겼다.

## Review

- 제출 링크에 저장소 URL과 핵심 파일 경로가 포함되어 있다.
- README의 실행 명령이 현재 폴더 구조와 일치한다.
- 검증 결과가 `examples/verification.md`에 기록되어 있다.
