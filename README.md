# torder-report-skillathon

![엑셀 팡션](https://mblogthumb-phinf.pstatic.net/MjAyNDAxMjdfMjAz/MDAxNzA2MzQ0ODYzNTQ5.k5znTy_B4NWJxAiSZbMrm4jLfHFC4d9qNh3DDBNESOQg.brZt2CeSDNaoK6phWAjWck2TBNR392p9KYwY1AKEbE8g.JPEG.vaipers/%EC%97%91%EC%85%80_%ED%8C%A1%EC%85%982.jpg?type=w800)
# 최대리. 내가 감히 조언하고 싶은게 있습니다. 코덱스 스킬? 그거 너무 믿지 마세요.고객 데이터를 엑셀 퐝션으로 하나 하나씩 분석하며 공감하는 방법도 있죠. 코덱스는 소잡는 칼 아닌가 싶어 의견드립니다.

이 스킬은 엑셀 분석으로 고생할 영업 사원들을 문서 작업으로부터 해방 시키고, 고객들과의 접점을 늘리고 유대 관계를 형성하는 것에 집중하길 바라며 만들었습니다.
즉, F&B 매장의 샘플 주문 CSV를 분석해 매장 사장님용 모바일 리포트를 만들고, Netlify 공유 URL과 Gmail 발송 초안까지 준비하는 Skillathon 제출용 스킬입니다.

본 스킬을 썼을 때 생성되는 결과물은 아래와 같습니다.

![티오더 리포트 미리보기](https://storage.ghost.io/c/a7/61/a761012a-4770-4f0e-ad76-0149eca2f048/content/images/2026/05/-----------------------------------------------------.png)

## 문제 정의

티오더를 설치한 뒤, 리텐션과 고객 간의 추천을 유도하려면 설치한 사장님에게 티오더의 효용성을 보여줘야 합니다.
이런 배경에서 티오더는 고객이 티오더를 설치하고 특정 기간(D+30)이 도래하면 로우 데이터를 분석해 고객께 리터치를 하며 티오더 사용 현황을 설명드리고 있습니다.

이 과정에서 매장 사장님에게 주문 데이터를 공유하려면 데이터를 분석하고, 보기 쉬운 리포트로 만들고, 공유 가능한 링크를 만들고, 발송 문구까지 작성해야 합니다. 이 과정은 반복적이지만 수작업이 많아 시간이 걸립니다.

따라서 스킬은 영업 담당자가 특정 기간 동안의 티오더 주문 CSV를 입력하고 스킬을 호출하기만 하면 다음 퍼널을 자동화합니다.

```text
티오더 주문 CSV
→ 매장별 인사이트 분석
→ 모바일 HTML 리포트 생성
→ Netlify 공유 URL 생성
→ Gmail 발송 초안 작성
→ 사용자가 검토 후 발송
```

## 제출 범위

- 실제 고객 데이터는 포함하지 않습니다.
- `mock-data/sample-orders.csv`로 실행 흐름을 재현합니다. 이 파일은 실제 CSV 형식을 유지하되 보안 컬럼을 더미 값으로 바꾼 샘플입니다.
- Netlify 배포는 공개 가능한 mock 리포트만 대상으로 합니다.
- Gmail은 실제 발송이 아니라 초안 생성까지만 다룹니다.

## 폴더 구조

```text
torder-report-skillathon/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── data-schema.md
│   ├── report-design.md
│   ├── netlify-deployment.md
│   ├── gmail-draft-workflow.md
│   └── validation-checklist.md
├── mock-data/
│   └── sample-orders.csv
├── scripts/
│   ├── analyze_orders.py
│   └── build_report.py
└── examples/
    ├── sample-analysis.json
    ├── sample-report.html
    ├── sample-email-draft.md
    └── verification.md
```

## 실행 방법

```bash
cd torder-report-skillathon
python3 scripts/analyze_orders.py mock-data/sample-orders.csv --out examples/sample-analysis.json
python3 scripts/build_report.py examples/sample-analysis.json --out examples/sample-report.html
```

생성된 `examples/sample-report.html`을 브라우저에서 열어 리포트를 확인합니다.

## Netlify 배포

Netlify CLI 또는 Netlify MCP를 사용할 수 있으면 `examples/sample-report.html`을 `index.html`로 배포합니다.

데모 URL:

https://torder-report-skillathon.netlify.app

```bash
mkdir -p /tmp/torder-report-skillathon-site
cp examples/sample-report.html /tmp/torder-report-skillathon-site/index.html
netlify deploy --dir /tmp/torder-report-skillathon-site --prod
```

배포 후 URL이 열리는지 확인합니다.

```bash
curl -L -s -o /tmp/torder-report-check.html -w "%{http_code}" "https://YOUR_SITE_URL"
```

## Gmail 초안

Gmail MCP가 연결되어 있으면 `references/gmail-draft-workflow.md` 기준으로 초안을 생성합니다. 연결되어 있지 않으면 `examples/sample-email-draft.md`처럼 발송 메시지를 파일 또는 응답으로 제공합니다.

실제 발송은 사용자가 직접 검토 후 진행합니다.

## 검증 결과

현재 샘플 기준 검증 결과는 `examples/verification.md`에 기록합니다.

## 샘플 데이터 비식별 처리

원본 CSV를 제출용 샘플로 바꿀 때는 아래 명령을 사용합니다.

```bash
python3 scripts/anonymize_orders.py /path/to/orders.csv --out mock-data/sample-orders.csv
```

다음 컬럼은 더미 값으로 치환됩니다.

- `주문ID`
- `매장코드`
- `태블릿 번호`
- `주문키`
- `ip`

## 한계

- mock data는 제출용 샘플이며 보안 컬럼을 더미화한 데이터입니다.
- Netlify와 Gmail은 계정 연결이 필요하므로 사용자의 승인과 인증이 필요합니다.
- 리포트 인사이트는 주문 CSV 기반의 운영 참고용이며 회계 자료로 사용하지 않습니다.
