"""PyKrx 기반 일봉 수집.

KRX 일봉 데이터를 가져와 prices 테이블 스키마에 맞는 list[dict]로 정규화한다.
ts는 거래일 00:00 KST를 UTC로 변환한 값으로 고정한다. 단일 시점만 있으면 충분하고
일봉 단위 분석에서 시각의 의미가 약하기 때문에 일자 앵커로 단순화.
"""

from __future__ import annotations

from datetime import datetime, time
from decimal import Decimal
from typing import TypedDict
from zoneinfo import ZoneInfo

from pykrx import stock

KST = ZoneInfo("Asia/Seoul")
UTC = ZoneInfo("UTC")


class PriceRow(TypedDict):
    symbol: str
    ts: datetime
    interval: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


def _to_decimal(v: object) -> Decimal:
    """pandas의 int/float/np.number를 안전하게 Decimal로. 문자열 경유로 부동소수점 오차 차단."""
    return Decimal(str(v))


def fetch_daily(symbol: str, fromdate: str, todate: str) -> list[PriceRow]:
    """일봉 수집.

    Args:
        symbol: KRX 종목 코드 6자리 (예: '005930')
        fromdate: 'YYYYMMDD'
        todate: 'YYYYMMDD' (포함)

    Returns:
        prices 스키마에 맞는 dict 리스트. 휴장일은 자동 제외(PyKrx가 빈 행을 안 줌).

    Raises:
        ValueError: 결과가 비어있으면(잘못된 종목코드 또는 휴장 구간) 즉시 에러.
    """
    df = stock.get_market_ohlcv(fromdate, todate, symbol)
    if df.empty:
        raise ValueError(f"빈 결과: symbol={symbol}, {fromdate}~{todate}")

    rows: list[PriceRow] = []
    for trade_date, r in df.iterrows():
        # PyKrx는 naive Timestamp(KST 의미)를 줌 → KST localize → UTC 변환
        kst_dt = datetime.combine(trade_date.date(), time(0, 0), tzinfo=KST)
        ts_utc = kst_dt.astimezone(UTC)

        rows.append(
            PriceRow(
                symbol=symbol,
                ts=ts_utc,
                interval="1d",
                open=_to_decimal(r["시가"]),
                high=_to_decimal(r["고가"]),
                low=_to_decimal(r["저가"]),
                close=_to_decimal(r["종가"]),
                volume=int(r["거래량"]),
            )
        )
    return rows
