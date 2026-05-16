#!/usr/bin/env python3
import argparse
import html
import json
from pathlib import Path


def won(value):
    return f"{int(value):,}원"


def bar_rows(hourly):
    if not hourly:
        return ""
    max_count = max(hourly.values())
    rows = []
    for hour, count in hourly.items():
        width = max(8, round(count / max_count * 100))
        rows.append(
            f"""
            <div class="bar-row">
              <span>{int(hour):02d}시</span>
              <div class="bar-track"><div class="bar" style="width:{width}%"></div></div>
              <strong>{count}건</strong>
            </div>
            """
        )
    return "\n".join(rows)


def daily_rows(daily_sales):
    if not daily_sales:
        return ""
    max_sales = max(daily_sales.values())
    rows = []
    for day, sales in daily_sales.items():
        label = day[5:].replace("-", "/")
        width = max(8, round(sales / max_sales * 100))
        rows.append(
            f"""
            <div class="bar-row daily">
              <span>{html.escape(label)}</span>
              <div class="bar-track"><div class="bar accent" style="width:{width}%"></div></div>
              <strong>{won(sales)}</strong>
            </div>
            """
        )
    return "\n".join(rows)


def menu_list(items):
    return "\n".join(
        f"""
        <li>
          <div>
            <strong>{html.escape(item['name'])}</strong>
            <span>{item['quantity']}개 판매</span>
          </div>
          <em>{won(item['sales'])}</em>
        </li>
        """
        for item in items
    )


def main():
    parser = argparse.ArgumentParser(description="Build mobile HTML report.")
    parser.add_argument("analysis_json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report-url", default="")
    args = parser.parse_args()

    data = json.loads(Path(args.analysis_json).read_text(encoding="utf-8"))
    metrics = data["metrics"]
    period = data["period"]
    report_url = args.report_url or "Netlify 배포 후 URL이 여기에 들어갑니다."

    insight_cards = "\n".join(
        f"""
        <section class="card">
          <p class="eyebrow">{html.escape(item['title'])}</p>
          <p>{html.escape(item['body'])}</p>
        </section>
        """
        for item in data["insights"]
    )

    menu_rows = menu_list(data["top_items"])
    revenue_rows = menu_list(data.get("top_revenue_items", []))

    document = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(data['store_name'])} 티오더 리포트</title>
  <style>
    :root {{
      --primary: #1456f0;
      --accent: #ff385c;
      --bg: #f4f6f8;
      --card: #ffffff;
      --text: #191f28;
      --muted: #6b7280;
      --line: #e5e7eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    main {{
      width: min(100%, 430px);
      margin: 0 auto;
      padding: 20px 16px 32px;
    }}
    .hero {{
      padding: 24px 20px;
      border-radius: 18px;
      background: linear-gradient(135deg, var(--primary), #0b2f88);
      color: white;
    }}
    .hero p {{ margin: 8px 0 0; opacity: .88; }}
    h1 {{ margin: 0; font-size: 26px; line-height: 1.2; }}
    h2 {{ margin: 28px 0 12px; font-size: 18px; }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-top: 12px;
    }}
    .metric, .card, .panel {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 16px;
    }}
    .metric span, .eyebrow {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .02em;
    }}
    .metric strong {{
      display: block;
      margin-top: 6px;
      font-size: 20px;
    }}
    .stack {{ display: grid; gap: 10px; }}
    ul {{ list-style: none; padding: 0; margin: 0; }}
    li {{
      display: flex;
      justify-content: space-between;
      gap: 14px;
      padding: 13px 0;
      border-bottom: 1px solid var(--line);
    }}
    li:last-child {{ border-bottom: 0; }}
    li span {{ display: block; color: var(--muted); font-size: 13px; }}
    li em {{ white-space: nowrap; font-style: normal; font-weight: 800; }}
    .bar-row {{
      display: grid;
      grid-template-columns: 42px 1fr 42px;
      align-items: center;
      gap: 10px;
      margin: 10px 0;
      font-size: 13px;
    }}
    .bar-track {{ height: 10px; border-radius: 999px; background: #e8eefc; overflow: hidden; }}
    .bar {{ height: 100%; border-radius: inherit; background: var(--primary); }}
    .bar.accent {{ background: var(--accent); }}
    .bar-row.daily {{ grid-template-columns: 48px 1fr 86px; }}
    .cta {{
      margin-top: 24px;
      padding: 18px;
      border-radius: 16px;
      background: #111827;
      color: white;
    }}
    .cta a {{ color: white; word-break: break-all; }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <h1>{html.escape(data['store_name'])}<br>티오더 주문 리포트</h1>
      <p>{period['start']} ~ {period['end']} 주문 데이터를 기준으로 정리했습니다.</p>
    </section>

    <section class="grid">
      <div class="metric"><span>총 주문 금액</span><strong>{won(metrics['total_sales'])}</strong></div>
      <div class="metric"><span>주문 세션</span><strong>{metrics['session_count']}건</strong></div>
      <div class="metric"><span>평균 주문 금액</span><strong>{won(metrics['avg_order_amount'])}</strong></div>
      <div class="metric"><span>추가 주문율</span><strong>{metrics['add_order_rate']}%</strong></div>
    </section>

    <h2>핵심 인사이트</h2>
    <div class="stack">{insight_cards}</div>

    <h2>인기 메뉴 TOP 5</h2>
    <section class="panel"><ul>{menu_rows}</ul></section>

    <h2>매출 기여 메뉴 TOP 5</h2>
    <section class="panel"><ul>{revenue_rows}</ul></section>

    <h2>일별 주문 금액</h2>
    <section class="panel">{daily_rows(data.get('daily_sales', {}))}</section>

    <h2>시간대별 주문 패턴</h2>
    <section class="panel">{bar_rows(data['hourly_orders'])}</section>

    <section class="cta">
      <strong>공유 URL</strong>
      <p>Netlify 배포 후 매장 사장님에게 아래 링크를 전달합니다.</p>
      <a href="{html.escape(report_url)}">{html.escape(report_url)}</a>
    </section>
  </main>
</body>
</html>
"""

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(document, encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
