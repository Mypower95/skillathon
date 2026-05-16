---
name: torder-report-skillathon
description: 티오더 주문 CSV를 분석해 매장 사장님용 모바일 HTML 리포트를 만들고, Netlify 공유 URL과 Gmail 발송 초안까지 준비하는 Skillathon 제출용 업무 자동화 스킬. 사용자가 티오더 주문 리포트, 매장 리포트, 사장님 공유 URL, Netlify 배포, Gmail 초안, 고객 발송 메시지를 요청하면 사용한다. 실제 고객 데이터 대신 mock data 또는 공개 가능한 샘플만 사용한다.
---

# 티오더 리포트 Skillathon

티오더 주문 CSV를 매장 사장님에게 바로 공유 가능한 리포트와 발송 초안으로 바꾼다.

## Guardrails

- 실제 고객명, 전화번호, 이메일, 주문 원본 등 민감 정보는 사용하지 않는다.
- 제출/데모에서는 `mock-data/sample-orders.csv` 또는 비식별 CSV만 사용한다.
- Netlify 배포 전 HTML에 민감 정보가 없는지 확인한다.
- Gmail은 초안 작성까지만 진행한다. 실제 발송은 사용자가 직접 검토 후 수행한다.
- API key, token, webhook URL, Gmail 인증 정보는 출력하지 않는다.

## Inputs

- 티오더 주문 CSV
- 선택 입력: 매장명, 리포트 기간, 수신자 이름, 수신자 이메일, 담당자명
- 선택 요청: Netlify 배포, Gmail 초안 생성, 발송 메시지 문구만 생성

CSV 컬럼은 `references/data-schema.md`를 따른다.

## Outputs

- 모바일 HTML 리포트
- 분석 결과 JSON
- Netlify 공유 URL 또는 수동 배포 안내
- Gmail 초안 또는 `examples/sample-email-draft.md` 형식의 발송 메시지
- 검증 결과 요약

## Workflow

1. CSV가 실제 고객 데이터인지 확인한다. 제출/데모라면 mock data만 사용한다.
2. 원본 CSV를 제출용 샘플로 바꿔야 하면 `scripts/anonymize_orders.py`로 보안 컬럼을 더미화한다.
3. `scripts/analyze_orders.py`로 주문 지표와 인사이트를 계산한다.
4. `scripts/build_report.py`로 모바일 HTML 리포트를 생성한다.
5. 사용자가 Netlify, URL, 링크, 공유를 요청했거나 제출 데모를 준비 중이면 Netlify 배포를 진행한다.
6. 배포 후 HTTPS URL이 HTTP 200으로 열리는지 확인한다.
7. Gmail 초안 요청이 있으면 `references/gmail-draft-workflow.md` 기준으로 고객별 발송 초안을 만든다.
8. 실제 발송은 하지 않고, 사용자가 검토해야 할 항목을 요약한다.

## Local Demo Commands

```bash
python3 scripts/anonymize_orders.py /path/to/orders.csv --out mock-data/sample-orders.csv
python3 scripts/analyze_orders.py mock-data/sample-orders.csv --out examples/sample-analysis.json
python3 scripts/build_report.py examples/sample-analysis.json --out examples/sample-report.html
```

## Netlify Deployment

Netlify 배포는 핵심 단계다. 절차와 실패 시 대안은 `references/netlify-deployment.md`를 따른다.

배포 전 확인:

- mock data만 포함됐는지 확인
- HTML에 이메일, 전화번호, 내부 URL, API key가 없는지 확인
- 파일명이 `index.html`인지 확인

배포 후 확인:

- URL이 HTTPS로 열리는지 확인
- HTTP 200 응답인지 확인
- 모바일 화면에서 핵심 지표와 CTA가 보이는지 확인

## Gmail Draft

Gmail MCP가 가능하면 draft를 생성한다. 도구가 없거나 연결되지 않았다면 `examples/sample-email-draft.md` 형식으로 초안만 작성한다.

메일 원칙:

- 제목에 매장명과 리포트 공유 목적을 포함한다.
- 본문은 5문장 이내로 짧게 쓴다.
- Netlify URL을 포함한다.
- 실제 발송은 사용자가 직접 한다.

## Quality Gate

완료 전 `references/validation-checklist.md`를 기준으로 확인한다.

필수 확인:

- CSV 분석 명령이 성공했다.
- HTML 리포트가 생성됐다.
- Netlify 배포 요청이 있으면 URL 검증 결과가 있다.
- Gmail 초안에는 수신자, 제목, 본문, 리포트 URL이 있다.
- 민감 정보가 포함되지 않았다.
