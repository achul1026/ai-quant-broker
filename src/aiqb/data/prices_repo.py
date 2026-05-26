"""prices 테이블 적재 헬퍼.

INSERT … ON CONFLICT UPDATE 패턴으로 멱등 적재.
재실행해도 동일 행이 누적되지 않고 최신 값으로 덮어쓰기 된다(데이터 정정 케이스 대응).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from aiqb.common.db import get_conn

if TYPE_CHECKING:
    from aiqb.data.pykrx_loader import PriceRow


_UPSERT_SQL = """
INSERT INTO prices (symbol, ts, interval, open, high, low, close, volume)
VALUES (%(symbol)s, %(ts)s, %(interval)s, %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s)
ON CONFLICT (symbol, interval, ts) DO UPDATE SET
    open   = EXCLUDED.open,
    high   = EXCLUDED.high,
    low    = EXCLUDED.low,
    close  = EXCLUDED.close,
    volume = EXCLUDED.volume
"""


def bulk_upsert_prices(rows: Sequence[PriceRow]) -> int:
    """rows를 prices 테이블에 일괄 적재. 반환값은 처리한 행 수.

    트랜잭션 단위: 1회 호출 = 1 트랜잭션. 부분 실패 시 전체 롤백.
    """
    if not rows:
        return 0

    with get_conn() as conn, conn.cursor() as cur:
        cur.executemany(_UPSERT_SQL, rows)
    return len(rows)
