#!/usr/bin/env python3
import argparse
import html
import json
import re
from datetime import date
from pathlib import Path


def won(value):
    return f"{int(value):,}원"


def parse_date(value):
    year, month, day = [int(part) for part in value.split("-")]
    return date(year, month, day)


def date_label(value):
    parsed = parse_date(value)
    return f"{parsed.month}/{parsed.day}"


def long_date(value):
    parsed = parse_date(value)
    return f"{parsed.year}년 {parsed.month}월 {parsed.day}일"


def period_text(period):
    start = parse_date(period["start"])
    end = parse_date(period["end"])
    days = (end - start).days + 1
    return f"{long_date(period['start'])} - {end.month}월 {end.day}일 · {days}일간"


def pct_change(first, last):
    if first == 0:
        return 0
    return round((last - first) / first * 100)


def store_heading(store_name):
    match = re.match(r"(.+?)\((.+?)\)$", store_name)
    if match:
        return f"{html.escape(match.group(1))}<br>{html.escape(match.group(2))}"
    return html.escape(store_name)


def rank_class(rank):
    if rank == 1:
        return "rank-1"
    if rank == 2:
        return "rank-2"
    if rank == 3:
        return "rank-3"
    return "rank-n"


def menu_rows(items):
    if not items:
        return ""
    max_qty = max(item["quantity"] for item in items) or 1
    rows = []
    for index, item in enumerate(items[:10], start=1):
        width = max(6, round(item["quantity"] / max_qty * 100))
        rows.append(
            f"""
      <div class="menu-item">
        <div class="menu-rank-badge {rank_class(index)}">{index}</div>
        <div class="menu-info">
          <p class="menu-name">{html.escape(item['name'])}</p>
          <div class="menu-bar-bg"><div class="menu-bar-fill" style="width:{width}%"></div></div>
        </div>
        <div class="menu-right">
          <p class="menu-count">{item['quantity']:,}<span class="menu-unit">개</span></p>
          <p class="menu-rev">{won(item['sales'])}</p>
        </div>
      </div>"""
        )
    return "\n".join(rows)


def insight_cards(data, add_order_sessions, daily_change, top_day_label):
    metrics = data["metrics"]
    top_items = data.get("top_items", [])
    revenue_items = data.get("top_revenue_items", [])
    add_order_rate = metrics["add_order_rate"]

    liquor_qty = sum(
        item["quantity"]
        for item in top_items
        if any(keyword in item["name"] for keyword in ("소주", "맥주", "참이슬", "새로", "카스", "테라", "처음처럼"))
    )
    liquor_name = next(
        (
            item["name"]
            for item in top_items
            if any(keyword in item["name"] for keyword in ("소주", "맥주", "참이슬", "새로", "카스", "테라", "처음처럼"))
        ),
        top_items[0]["name"] if top_items else "인기 메뉴",
    )
    revenue_item = revenue_items[0] if revenue_items else top_items[0]

    cards = [
        (
            "주류 반응",
            f"{html.escape(liquor_name)} 중심으로 주류/음료가 <strong>{liquor_qty:,}개</strong> 판매됐습니다. 추가 주문율 <strong>{add_order_rate}%</strong>와 함께 객단가를 끌어올리는 흐름이 보입니다.",
        ),
        (
            "단가 기여",
            f"{html.escape(revenue_item['name'])}이 매출 <strong>{won(revenue_item['sales'])}</strong>을 만들며 단가 기여도가 높았습니다. 수량 TOP 메뉴와 함께 묶음 제안하기 좋습니다.",
        ),
        (
            "매출 추이",
            f"첫날 대비 마지막 날 매출은 <strong>{daily_change:+,}%</strong> 변화했습니다. 기간 내 최고 매출일은 <strong>{top_day_label}</strong>입니다.",
        ),
    ]

    return "\n".join(
        f"""
    <div class="insight-card">
      <p class="insight-title">{title}</p>
      <p class="insight-body">{body}</p>
    </div>"""
        for title, body in cards
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
    daily_sales = data.get("daily_sales", {})
    hourly_orders = data.get("hourly_orders", {})

    daily_labels = [date_label(day) for day in daily_sales.keys()]
    daily_amounts = list(daily_sales.values())
    hourly_labels = [f"{int(hour)}시" for hour in hourly_orders.keys()]
    hourly_counts = list(hourly_orders.values())

    first_sales = daily_amounts[0] if daily_amounts else 0
    last_sales = daily_amounts[-1] if daily_amounts else 0
    daily_change = pct_change(first_sales, last_sales)
    top_day, top_day_sales = max(daily_sales.items(), key=lambda item: item[1])
    top_day_label = date_label(top_day)

    peak_hour, peak_count = max(hourly_orders.items(), key=lambda item: item[1])
    total_hourly = sum(hourly_orders.values()) or 1
    peak_share = round(peak_count / total_hourly * 100)

    session_count = metrics["session_count"]
    add_order_rate = metrics["add_order_rate"]
    add_order_sessions = round(session_count * add_order_rate / 100)
    ring_offset = round(175.9 * (1 - add_order_rate / 100), 1)
    avg_daily_sales = round(metrics["total_sales"] / max(len(daily_sales), 1))

    document = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>{html.escape(data['store_name'])} · 티오더 리포트</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
  :root {{
    --bg: #F5F6F8; --card: #FFFFFF; --primary: #FF193F; --primary-light: #FFF0F2;
    --sub: #6DA7F8; --sub-light: #EEF5FF; --text1: #191F28; --text2: #4E5968;
    --text3: #8B95A1; --border: #F2F4F6; --radius: 16px; --radius-sm: 10px;
  }}
  html, body {{ background: var(--bg); font-family: -apple-system, 'Apple SD Gothic Neo', 'Pretendard', sans-serif; color: var(--text1); min-height: 100vh; }}
  .page {{ max-width: 480px; margin: 0 auto; padding: 0 0 40px; }}
  .header {{ background: var(--card); padding: 56px 20px 24px; border-bottom: 1px solid var(--border); }}
  .header-badge {{ display: inline-flex; align-items: center; gap: 5px; background: var(--primary-light); color: var(--primary); font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 20px; margin-bottom: 12px; }}
  .header-badge span {{ width: 6px; height: 6px; background: var(--primary); border-radius: 50%; display: inline-block; }}
  .header h1 {{ font-size: 22px; font-weight: 700; color: var(--text1); line-height: 1.3; margin-bottom: 4px; }}
  .header-period {{ font-size: 14px; color: var(--text3); }}
  .section {{ padding: 24px 20px 0; }}
  .section-label {{ font-size: 13px; font-weight: 600; color: var(--text3); letter-spacing: 0.03em; margin-bottom: 12px; }}
  .highlight-card {{ background: var(--primary); border-radius: var(--radius); padding: 24px 20px; color: white; margin-bottom: 16px; }}
  .hl-label {{ font-size: 13px; opacity: 0.75; margin-bottom: 6px; }}
  .hl-amount {{ font-size: 34px; font-weight: 700; margin-bottom: 4px; }}
  .hl-sub {{ font-size: 13px; opacity: 0.7; }}
  .summary-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
  .summary-card {{ background: var(--card); border-radius: var(--radius-sm); padding: 16px; }}
  .sc-label {{ font-size: 12px; color: var(--text3); margin-bottom: 6px; }}
  .sc-value {{ font-size: 20px; font-weight: 700; color: var(--text1); }}
  .sc-unit {{ font-size: 13px; font-weight: 400; color: var(--text2); margin-left: 2px; }}
  .effect-card {{ background: var(--primary-light); border-radius: var(--radius); padding: 20px; display: flex; align-items: center; gap: 16px; }}
  .effect-ring {{ position: relative; width: 72px; height: 72px; flex-shrink: 0; }}
  .effect-ring svg {{ width: 72px; height: 72px; transform: rotate(-90deg); }}
  .effect-ring-text {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
  .effect-ring-pct {{ font-size: 18px; font-weight: 700; color: var(--primary); line-height: 1; }}
  .effect-ring-sub {{ font-size: 9px; color: var(--primary); opacity: 0.8; margin-top: 1px; }}
  .effect-desc {{ flex: 1; }}
  .effect-title {{ font-size: 15px; font-weight: 700; color: var(--text1); margin-bottom: 4px; }}
  .effect-body {{ font-size: 13px; color: var(--text2); line-height: 1.6; }}
  .effect-body strong, .chart-note strong, .insight-body strong {{ color: var(--primary); font-weight: 700; }}
  .chart-card {{ background: var(--card); border-radius: var(--radius); padding: 20px; }}
  .chart-canvas-wrap {{ position: relative; width: 100%; }}
  .chart-note {{ font-size: 12px; color: var(--text3); text-align: right; padding-top: 10px; border-top: 1px solid var(--border); margin-top: 10px; }}
  .peak-note {{ margin-top: 12px; background: var(--sub-light); border-radius: var(--radius-sm); padding: 10px 14px; font-size: 13px; color: var(--sub); font-weight: 600; }}
  .menu-wrap {{ background: var(--card); border-radius: var(--radius); overflow: hidden; }}
  .menu-item {{ display: flex; align-items: center; padding: 14px 20px; border-bottom: 1px solid var(--border); gap: 12px; }}
  .menu-item:last-child {{ border-bottom: none; }}
  .menu-rank-badge {{ width: 24px; height: 24px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; }}
  .rank-1 {{ background: #FFF0D4; color: #D4820A; }}
  .rank-2 {{ background: #F0F0F0; color: #666; }}
  .rank-3 {{ background: #FDEAE6; color: #C0392B; }}
  .rank-n {{ background: var(--border); color: var(--text3); }}
  .menu-info {{ flex: 1; min-width: 0; }}
  .menu-name {{ font-size: 14px; font-weight: 600; color: var(--text1); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px; }}
  .menu-bar-bg {{ height: 4px; background: var(--border); border-radius: 2px; }}
  .menu-bar-fill {{ height: 4px; background: var(--sub); border-radius: 2px; }}
  .menu-right {{ text-align: right; flex-shrink: 0; }}
  .menu-count {{ font-size: 15px; font-weight: 700; color: var(--text1); }}
  .menu-unit, .menu-rev {{ font-size: 12px; color: var(--text3); }}
  .menu-rev {{ margin-top: 2px; }}
  .insight-card {{ background: var(--card); border-radius: var(--radius); padding: 18px 20px; }}
  .insight-card + .insight-card {{ margin-top: 10px; }}
  .insight-title {{ font-size: 14px; font-weight: 700; color: var(--text1); margin-bottom: 4px; }}
  .insight-body {{ font-size: 13px; color: var(--text2); line-height: 1.6; }}
  .footer {{ padding: 24px 20px 0; text-align: center; }}
  .footer-logo {{ font-size: 13px; font-weight: 700; color: var(--text3); }}
  .footer-logo span {{ color: var(--primary); }}
  .footer-note {{ font-size: 11px; color: var(--text3); margin-top: 6px; line-height: 1.6; }}
  @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: translateY(0); }} }}
  .fade-up {{ animation: fadeUp 0.5s ease forwards; opacity: 0; }}
  .delay-1 {{ animation-delay: 0.1s; }} .delay-2 {{ animation-delay: 0.2s; }} .delay-3 {{ animation-delay: 0.3s; }} .delay-4 {{ animation-delay: 0.4s; }} .delay-5 {{ animation-delay: 0.5s; }}
</style>
</head>
<body>
<div class="page">
  <div class="header fade-up">
    <div class="header-badge"><span></span> 티오더 주문 리포트</div>
    <h1>{store_heading(data['store_name'])}</h1>
    <p class="header-period">{period_text(period)}</p>
  </div>
  <div class="section fade-up delay-1">
    <div class="section-label">총 거래액</div>
    <div class="highlight-card">
      <p class="hl-label">티오더를 통한 기간 누적 매출</p>
      <p class="hl-amount">{won(metrics['total_sales'])}</p>
      <p class="hl-sub">일평균 {won(avg_daily_sales)} · 총 {session_count:,}개 테이블</p>
    </div>
    <div class="summary-grid">
      <div class="summary-card"><p class="sc-label">테이블 세션</p><p class="sc-value">{session_count:,}<span class="sc-unit">건</span></p></div>
      <div class="summary-card"><p class="sc-label">평균 객단가</p><p class="sc-value">{won(metrics['avg_order_amount']).replace('원', '')}<span class="sc-unit">원</span></p></div>
    </div>
  </div>
  <div class="section fade-up delay-2">
    <div class="section-label">티오더 핵심 효과</div>
    <div class="effect-card">
      <div class="effect-ring">
        <svg viewBox="0 0 72 72">
          <circle cx="36" cy="36" r="28" fill="none" stroke="#FFD6DC" stroke-width="8"/>
          <circle cx="36" cy="36" r="28" fill="none" stroke="#FF193F" stroke-width="8" stroke-dasharray="175.9" stroke-dashoffset="{ring_offset}" stroke-linecap="round"/>
        </svg>
        <div class="effect-ring-text"><span class="effect-ring-pct">{add_order_rate:g}%</span><span class="effect-ring-sub">추가주문</span></div>
      </div>
      <div class="effect-desc">
        <p class="effect-title">추가 주문율 {add_order_rate:g}%</p>
        <p class="effect-body">{session_count:,}개 테이블 중 <strong>{add_order_sessions:,}개</strong>에서 착석 후 추가 주문 발생. 직원 호출 없이 자연스럽게 매출이 늘어납니다.</p>
      </div>
    </div>
  </div>
  <div class="section fade-up delay-3">
    <div class="section-label">일별 매출 추이</div>
    <div class="chart-card">
      <div class="chart-canvas-wrap" style="height:160px;"><canvas id="dailyChart"></canvas></div>
      <p class="chart-note">{daily_labels[0]} 대비 {daily_labels[-1]} <strong>{daily_change:+,}% 변화</strong></p>
    </div>
  </div>
  <div class="section fade-up delay-3">
    <div class="section-label">시간대별 주문 패턴</div>
    <div class="chart-card">
      <div class="chart-canvas-wrap" style="height:120px;"><canvas id="hourlyChart"></canvas></div>
      <div class="peak-note">피크타임 {int(peak_hour)}시 · 전체 주문의 {peak_share}% 집중</div>
    </div>
  </div>
  <div class="section fade-up delay-4">
    <div class="section-label">메뉴별 판매 순위 · TOP 10</div>
    <div class="menu-wrap">
{menu_rows(data.get('top_items', []))}
    </div>
  </div>
  <div class="section fade-up delay-5">
    <div class="section-label">주요 인사이트</div>
{insight_cards(data, add_order_sessions, daily_change, top_day_label)}
  </div>
  <div class="footer">
    <p class="footer-logo"><span>t'order</span> multi order report</p>
    <p class="footer-note">티오더의 멀티오더(NFC/QR오더) 주문 데이터 기준<br>테이블 세션은 고유 주문ID 기준으로 집계했습니다.</p>
  </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script>
const dailyLabels = {json.dumps(daily_labels, ensure_ascii=False)};
const dailyAmounts = {json.dumps(daily_amounts, ensure_ascii=False)};
const hourlyLabels = {json.dumps(hourly_labels, ensure_ascii=False)};
const hourlyCounts = {json.dumps(hourly_counts, ensure_ascii=False)};
Chart.defaults.font.family = "-apple-system, Apple SD Gothic Neo, Pretendard, sans-serif";
new Chart(document.getElementById('dailyChart'), {{
  type: 'bar',
  data: {{ labels: dailyLabels, datasets: [{{ data: dailyAmounts, backgroundColor: '#FF193F', borderRadius: 6, barThickness: 18 }}] }},
  options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: ctx => Number(ctx.raw).toLocaleString('ko-KR') + '원' }} }} }}, scales: {{ x: {{ grid: {{ display: false }}, ticks: {{ color: '#8B95A1', font: {{ size: 11 }} }} }}, y: {{ beginAtZero: true, grid: {{ color: '#F2F4F6' }}, ticks: {{ color: '#8B95A1', font: {{ size: 10 }}, callback: v => Math.round(v / 10000) + '만' }} }} }} }}
}});
new Chart(document.getElementById('hourlyChart'), {{
  type: 'bar',
  data: {{ labels: hourlyLabels, datasets: [{{ data: hourlyCounts, backgroundColor: '#6DA7F8', borderRadius: 5, barThickness: 14 }}] }},
  options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: ctx => Number(ctx.raw).toLocaleString('ko-KR') + '건' }} }} }}, scales: {{ x: {{ grid: {{ display: false }}, ticks: {{ color: '#8B95A1', font: {{ size: 10 }} }} }}, y: {{ beginAtZero: true, grid: {{ color: '#F2F4F6' }}, ticks: {{ precision: 0, color: '#8B95A1', font: {{ size: 10 }} }} }} }} }}
}});
</script>
</body>
</html>
"""

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(document, encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
