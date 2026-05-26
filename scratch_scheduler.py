from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from aiqb.data.pykrx_loader import fetch_daily
from aiqb.data.prices_repo import bulk_upsert_prices

KST = ZoneInfo("Asia/Seoul")
scheduler = BlockingScheduler(timezone="Asia/Seoul")


@scheduler.scheduled_job(CronTrigger(second=0))
def ingest_job():
    # 학습 단계라 검증된 구간으로 고정. 다음 Step에서 "오늘"로 교체.
    symbol = "005930"
    fromdate, todate = "20240101", "20240131"

    now_str = datetime.now(KST).strftime("%H:%M:%S")
    print(f"[{now_str}] {symbol} {fromdate}~{todate} 적재 시작")

    rows = fetch_daily(symbol, fromdate, todate)
    n = bulk_upsert_prices(rows)
    print(f"  → 완료 rows={n}")


print("스케줄러 시작. Ctrl+C로 종료.")
scheduler.start()