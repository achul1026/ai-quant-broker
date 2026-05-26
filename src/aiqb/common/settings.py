"""애플리케이션 설정.

`.env` 파일과 환경변수에서 값을 로드하고 Pydantic으로 타입·검증을 보장한다.
시크릿(API Key 등)은 `SecretStr`로 감싸 실수로 로그·repr에 노출되지 않게 한다.

사용 예:
    from aiqb.common.settings import settings
    print(settings.db.host)
    api_key = settings.openai_api_key.get_secret_value()
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """TimescaleDB(PostgreSQL) 접속 정보."""

    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")

    host: str = "localhost"
    port: int = 5432
    name: str
    user: str
    password: SecretStr

    @property
    def dsn(self) -> str:
        """psycopg가 읽는 표준 PostgreSQL DSN. 비밀번호는 get_secret_value()로 추출."""
        return (
            f"postgresql://{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class KISSettings(BaseSettings):
    """한국투자증권 OpenAPI 자격 정보 (Phase 4에서 본격 사용)."""

    model_config = SettingsConfigDict(env_prefix="KIS_", env_file=".env", extra="ignore")

    app_key: SecretStr = SecretStr("")
    app_secret: SecretStr = SecretStr("")
    account_no: str = ""
    account_product_code: str = ""
    mode: Literal["paper", "real"] = "paper"


class Settings(BaseSettings):
    """루트 설정 컨테이너.

    하위 도메인별 Settings를 합성한다. LLM 키처럼 단일 값은 여기서 바로 들고,
    DB/KIS처럼 prefix가 공유되는 묶음은 별도 클래스로 분리.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    kis: KISSettings = Field(default_factory=KISSettings)

    openai_api_key: SecretStr = SecretStr("")
    anthropic_api_key: SecretStr = SecretStr("")
    slack_webhook_url: SecretStr = SecretStr("")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """프로세스 수명 동안 1회만 로드. 테스트에서는 cache_clear()로 초기화."""
    return Settings()


settings = get_settings()
