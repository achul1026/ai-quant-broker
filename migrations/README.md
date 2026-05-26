# Migrations

SQL 파일 기반 마이그레이션. Alembic 미사용(P1-1 시점 결정 — `projects/ai-quant-broker.md` ADR 참고).

## 명명 규칙

```
V<NNN>__<snake_case_subject>.sql
```

- `V001__init.sql`, `V002__add_news_table.sql` …
- 번호는 순서 보장용 zero-pad 3자리.
- 한 파일은 idempotent하지 않아도 OK (한 번만 실행되는 전제).

## 실행 방법

컨테이너 안에서 `psql`로 직접 실행한다. 컨테이너의 `/migrations` 경로에 호스트의 `migrations/`가 마운트되어 있다.

```bash
# 단일 파일 실행
docker compose exec timescaledb psql -U "$DB_USER" -d "$DB_NAME" -f /migrations/V001__init.sql

# 적용 이력은 본인이 관리. 추후 schema_migrations 테이블을 도입할지 결정.
```

## 권장 첫 마이그레이션 (V001__init.sql)

- `CREATE EXTENSION IF NOT EXISTS timescaledb;`
- 주가 테이블 생성 (예: `prices(symbol, ts, open, high, low, close, volume)`)
- hypertable 변환 (`SELECT create_hypertable('prices', 'ts');`)
- 자주 쓰는 인덱스 (symbol, ts DESC 등)

스키마 설계 자체는 학습 모드에 따라 직접 작성. 막히면 컬럼 후보·인덱스 트레이드오프만 물어봐.

## 적용 이력 관리

현재는 수기 관리. 마이그레이션이 5~10개를 넘기 시작하면 `schema_migrations` 테이블 또는 Alembic 승격 검토.
