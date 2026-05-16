# Netlify Deployment

Netlify 배포는 이 스킬의 핵심 단계다. 리포트를 파일로 끝내지 않고 매장 사장님에게 바로 공유 가능한 URL로 만드는 것이 목적이다.

## Preflight

- 배포 대상은 mock data 기반 HTML이어야 한다.
- HTML에 API key, token, webhook URL, 이메일, 전화번호, 실제 고객 정보가 없어야 한다.
- 배포 폴더에는 `index.html`만 있어도 충분하다.

## Netlify CLI Flow

```bash
mkdir -p /tmp/torder-report-skillathon-site
cp examples/sample-report.html /tmp/torder-report-skillathon-site/index.html
netlify deploy --dir /tmp/torder-report-skillathon-site --prod
```

Netlify 로그인이 필요하면 사용자가 직접 로그인과 권한 승인을 한다.

## Netlify MCP Flow

Netlify 도구가 연결되어 있으면 다음 순서로 진행한다.

1. Netlify 계정 연결 상태를 확인한다.
2. 새 프로젝트 또는 제출용 사이트를 만든다.
3. `index.html`이 있는 폴더를 배포한다.
4. `siteUrl`을 기록한다.
5. HTTPS URL을 열어 HTTP 200인지 확인한다.

## Verification

```bash
curl -L -s -o /tmp/torder-report-check.html -w "%{http_code}" "https://YOUR_SITE_URL"
```

결과가 `200`이면 배포 URL 검증을 통과한 것으로 기록한다.

## Fallback

Netlify 계정 연결이 안 되어 있으면 HTML 파일 생성까지만 검증하고, README에 수동 배포 절차와 미실행 사유를 남긴다.
