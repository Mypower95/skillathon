#!/usr/bin/env python3
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


def money(value):
    return int(str(value).replace(",", "").strip())


def parse_dt(value):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise ValueError(f"Unsupported datetime format: {value}")


def parse_cart(cart):
    items = []
    for raw in re.findall(r"\[(.+?)\]", cart or ""):
        match = re.match(r"(.+?)\s+\(([^()]*)\)\s+\((\d+)개\)\s+\((\d+)원\)", raw.strip())
        if not match:
            continue
        name, item_code, qty, price = match.groups()
        items.append(
            {
                "item_name": name.strip(),
                "item_code": item_code.strip(),
                "quantity": int(qty),
                "unit_price": money(price),
            }
        )
    return items


def normalize_rows(csv_path):
    normalized = []
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        korean_schema = {"주문시간", "주문ID", "상호지점명", "장바구니", "주문 장바구니 전체 금액"}.issubset(fields)

        for row in reader:
            if korean_schema:
                parsed_items = parse_cart(row["장바구니"])
                if parsed_items:
                    for item in parsed_items:
                        normalized.append(
                            {
                                "order_id": row["주문ID"],
                                "store_name": row["상호지점명"],
                                "ordered_at": row["주문시간"],
                                "item_name": item["item_name"],
                                "quantity": item["quantity"],
                                "unit_price": item["unit_price"],
                                "channel": row.get("주문 유형", "unknown"),
                                "order_total": money(row["주문 장바구니 전체 금액"]),
                                "pos_status": row.get("최종 포스 연동 여부", ""),
                                "pos_response_seconds": row.get("포스 응답 소요 시간", ""),
                            }
                        )
                else:
                    normalized.append(
                        {
                            "order_id": row["주문ID"],
                            "store_name": row["상호지점명"],
                            "ordered_at": row["주문시간"],
                            "item_name": "미분류",
                            "quantity": 1,
                            "unit_price": money(row["주문 장바구니 전체 금액"]),
                            "channel": row.get("주문 유형", "unknown"),
                            "order_total": money(row["주문 장바구니 전체 금액"]),
                            "pos_status": row.get("최종 포스 연동 여부", ""),
                            "pos_response_seconds": row.get("포스 응답 소요 시간", ""),
                        }
                    )
            else:
                normalized.append(
                    {
                        "order_id": row["order_id"],
                        "store_name": row["store_name"],
                        "ordered_at": row["ordered_at"],
                        "item_name": row["item_name"],
                        "quantity": int(row["quantity"]),
                        "unit_price": money(row["unit_price"]),
                        "channel": row.get("channel", "unknown"),
                        "order_total": None,
                        "pos_status": row.get("pos_status", ""),
                        "pos_response_seconds": row.get("pos_response_seconds", ""),
                    }
                )
    return normalized


def main():
    parser = argparse.ArgumentParser(description="Analyze mock Torder order CSV.")
    parser.add_argument("csv_path")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    rows = normalize_rows(args.csv_path)
    for row in rows:
        row["amount"] = row["quantity"] * row["unit_price"]
        row["dt"] = parse_dt(row["ordered_at"])

    if not rows:
        raise SystemExit("CSV has no rows.")

    sessions = defaultdict(list)
    item_qty = Counter()
    item_sales = Counter()
    hourly = Counter()
    daily_sales = Counter()
    order_type = Counter()
    pos_status = Counter()

    for row in rows:
        sessions[row["order_id"]].append(row)
        item_qty[row["item_name"]] += row["quantity"]
        item_sales[row["item_name"]] += row["amount"]
        hourly[row["dt"].hour] += 1
        daily_sales[row["dt"].date().isoformat()] += row["amount"]
        order_type[row["channel"]] += 1
        if row["pos_status"]:
            pos_status[row["pos_status"]] += 1

    total_sales = sum(row["amount"] for row in rows)
    session_count = len(sessions)
    add_order_sessions = sum(1 for items in sessions.values() if len(items) >= 2)
    add_order_rate = round(add_order_sessions / session_count * 100, 1)
    avg_order_amount = round(total_sales / session_count)
    dates = sorted({row["dt"].date().isoformat() for row in rows})
    peak_hour, peak_orders = hourly.most_common(1)[0]

    top_items = [
        {"name": name, "quantity": qty, "sales": item_sales[name]}
        for name, qty in item_qty.most_common(5)
    ]
    top_revenue_items = [
        {"name": name, "quantity": item_qty[name], "sales": sales}
        for name, sales in item_sales.most_common(5)
    ]

    insights = [
        {
            "title": "추가 주문",
            "body": f"고유 주문 {session_count}건 중 {add_order_sessions}건에서 추가 주문이 발생했습니다.",
        },
        {
            "title": "인기 메뉴",
            "body": f"가장 많이 팔린 메뉴는 {top_items[0]['name']}이며 총 {top_items[0]['quantity']}개 판매되었습니다.",
        },
        {
            "title": "피크 시간",
            "body": f"{peak_hour}시에 주문이 {peak_orders}건으로 가장 많았습니다.",
        },
    ]
    if top_revenue_items and top_revenue_items[0]["name"] != top_items[0]["name"]:
        insights.append(
            {
                "title": "매출 기여",
                "body": f"매출 기여가 가장 큰 메뉴는 {top_revenue_items[0]['name']}입니다.",
            }
        )

    result = {
        "store_name": rows[0]["store_name"],
        "period": {"start": dates[0], "end": dates[-1]},
        "metrics": {
            "total_sales": total_sales,
            "session_count": session_count,
            "avg_order_amount": avg_order_amount,
            "add_order_rate": add_order_rate,
        },
        "top_items": top_items,
        "top_revenue_items": top_revenue_items,
        "hourly_orders": dict(sorted(hourly.items())),
        "daily_sales": dict(sorted(daily_sales.items())),
        "order_type": dict(order_type.most_common()),
        "pos_status": dict(pos_status.most_common()),
        "insights": insights,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
