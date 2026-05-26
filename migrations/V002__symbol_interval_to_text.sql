-- V002__symbol_interval_to_text.sql
-- VARCHAR(n) → TEXT 전환.
-- PostgreSQL에서 VARCHAR(n)과 TEXT는 저장·성능 동등하며 TEXT가 모던 컨벤션.
-- 길이 제약은 도메인상 의미가 약해(symbol·interval 모두 짧은 식별자) 별도 CHECK는 두지 않는다.
-- 안전성: VARCHAR(n) → TEXT는 PostgreSQL이 데이터 재작성 없이 카탈로그만 수정하는 케이스다(짧은 락).

ALTER TABLE prices ALTER COLUMN symbol   TYPE TEXT;
ALTER TABLE prices ALTER COLUMN interval TYPE TEXT;
