"""ETL 엔트리 포인트.

사용:
    uv run python -m aiqb.data.ingest 005930 20240101 20240131
"""

from __future__ import annotations

import argparse
import sys

from aiqb.data.pykrx_loader import fetch_daily
from aiqb.data.prices_repo import bulk_upsert_prices


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="KRX 일봉 수집·적재")
    parser.add_argument("symbol", help="종목 코드 6자리 (예: 005930)")
    parser.add_argument("fromdate", help="시작일 YYYYMMDD")
    parser.add_argument("todate", help="종료일 YYYYMMDD (포함)")
    args = parser.parse_args(argv)

    rows = fetch_daily(args.symbol, args.fromdate, args.todate)
    n = bulk_upsert_prices(rows)
    print(f"적재 완료: symbol={args.symbol} rows={n} (구간 {args.fromdate}~{args.todate})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
