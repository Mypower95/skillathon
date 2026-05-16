# Verification

이 파일은 Skillathon 제출 전 실행 결과를 기록한다.

## Local Commands

```bash
python3 scripts/anonymize_orders.py /path/to/orders.csv --out mock-data/sample-orders.csv
python3 scripts/analyze_orders.py mock-data/sample-orders.csv --out examples/sample-analysis.json
python3 scripts/build_report.py examples/sample-analysis.json --out examples/sample-report.html
```

## Results

- CSV 비식별 처리: passed
- CSV 분석: passed
- HTML 리포트 생성: passed
- Santana-style UX/UI alignment: passed
- Chart.js daily/hourly charts: passed
- Menu ranking TOP 10: passed
- Netlify 배포: passed
- Netlify URL 검증: passed
- Gmail 초안 생성: sample draft only

## Data Safety

- mock data only
- no API keys
- no customer phone numbers
- no real customer emails
- `주문ID`, `매장코드`, `태블릿 번호`, `주문키`, `ip` anonymized

## Generated Files

- `examples/sample-analysis.json`
- `examples/sample-report.html`
- `examples/sample-email-draft.md`

## Netlify

- Project: `torder-report-skillathon`
- Site URL: https://torder-report-skillathon.netlify.app
- Deploy ID: `6a08249b7b6b97dd0c183817`
- HTTP check: `200`

## Sample Metrics

- Rows: 1,016
- Period: 2026-04-21 ~ 2026-05-11
- Store: 코덱스커뮤니티(최고점)
- Total sales: 17,753,900원
- Order sessions: 534
- Add-order rate: 94.2%
