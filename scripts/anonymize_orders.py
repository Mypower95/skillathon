#!/usr/bin/env python3
import argparse
import csv
import hashlib
from pathlib import Path


SENSITIVE_COLUMNS = {
    "주문ID": "ORDER",
    "매장코드": "STORE",
    "태블릿번호": "TABLET",
    "태블릿 번호": "TABLET",
    "주문키": "KEY",
    "ip": "IP",
}


def token(value, prefix, width=6):
    if not value:
        return ""
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"{prefix}-{int(digest[:12], 16) % (10 ** width):0{width}d}"


def main():
    parser = argparse.ArgumentParser(description="Anonymize Torder order CSV for Skillathon demo.")
    parser.add_argument("input_csv")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    in_path = Path(args.input_csv)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    maps = {column: {} for column in SENSITIVE_COLUMNS}
    with open(in_path, encoding="utf-8-sig", newline="") as src, open(
        out_path, "w", encoding="utf-8-sig", newline=""
    ) as dst:
        reader = csv.DictReader(src)
        writer = csv.DictWriter(dst, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            for column, prefix in SENSITIVE_COLUMNS.items():
                if column not in row:
                    continue
                value = row[column]
                if value not in maps[column]:
                    maps[column][value] = token(value, prefix)
                row[column] = maps[column][value]
            writer.writerow(row)

    print(f"Wrote anonymized CSV to {out_path}")


if __name__ == "__main__":
    main()
