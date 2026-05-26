-- V001__init.sql
-- TimescaleDB 확장 + 주가 시계열 테이블 초기 스키마

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 주가 테이블 (일봉·분봉 공용)
-- 설계 의도:
--   symbol VARCHAR(20): 한국 6자리 종목코드 + ".KS"/".KQ" 같은 거래소 suffix와 해외 ticker 확장 대비.
--   ts TIMESTAMPTZ: 타임존 인식. KST 거래시간을 UTC로 정규화 저장. 컨테이너 TZ=Asia/Seoul과 별개로 데이터는 UTC.
--   interval VARCHAR(8): '1d', '1m', '5m' 등 봉 단위. 한 테이블에 다양한 봉을 보관 (Phase 1 단순화).
--   NUMERIC(20,4): float 부동소수점 오차 회피. 원/달러 단위 4자리 소수까지 안전.
--   volume BIGINT: 대형주 일거래량이 INTEGER(약 21억) 한계 근접 가능.
CREATE TABLE prices (
    symbol      VARCHAR(20)    NOT NULL,
    ts          TIMESTAMPTZ    NOT NULL,
    interval    VARCHAR(8)     NOT NULL,
    open        NUMERIC(20,4)  NOT NULL,
    high        NUMERIC(20,4)  NOT NULL,
    low         NUMERIC(20,4)  NOT NULL,
    close       NUMERIC(20,4)  NOT NULL,
    volume      BIGINT         NOT NULL,
    PRIMARY KEY (symbol, interval, ts)
);

-- hypertable 변환
-- chunk_time_interval 7 days: 일봉 기준 약 5개 봉, 분봉 기준 약 2,000봉/종목.
-- 너무 크면 chunk 한 개가 비대해지고, 너무 작으면 chunk 수가 폭증해 쿼리 플래너 부담.
-- 운용하며 데이터량 보고 조정.
SELECT create_hypertable('prices', 'ts', chunk_time_interval => INTERVAL '7 days');

-- 자주 쓸 쿼리: "특정 종목의 최근 N봉" → (symbol, interval, ts DESC) 인덱스가 효율적
-- PRIMARY KEY 인덱스가 (symbol, interval, ts ASC)이므로 별도 DESC 인덱스 추가.
CREATE INDEX idx_prices_symbol_interval_ts_desc
    ON prices (symbol, interval, ts DESC);
