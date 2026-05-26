"""DB 커넥션 헬퍼.

psycopg v3 + 커넥션 풀 기반. 짧은 스크립트(ETL)부터 장기 운용 루프까지
같은 인터페이스로 사용하기 위해 풀 싱글톤을 둔다.

사용 예:
    from aiqb.common.db import get_conn

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            print(cur.fetchone())
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache

import psycopg
from psycopg_pool import ConnectionPool

from aiqb.common.settings import settings


@lru_cache(maxsize=1)
def get_pool() -> ConnectionPool:
    """프로세스당 1회 생성. 풀 크기는 ETL 단계 기준 보수적으로 설정.

    Phase 3 백테스트 병렬화나 Phase 4 운용 루프에서 max_size 상향이 필요할 수 있다.
    """
    pool = ConnectionPool(
        conninfo=settings.db.dsn,
        min_size=1,
        max_size=5,
        kwargs={"autocommit": False},
    )
    pool.wait(timeout=10)
    return pool


@contextmanager
def get_conn() -> Iterator[psycopg.Connection]:
    """풀에서 커넥션 1개를 빌려 사용. 블록 종료 시 자동 반환·커밋."""
    with get_pool().connection() as conn:
        yield conn
