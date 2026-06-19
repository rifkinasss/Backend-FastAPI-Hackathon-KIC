from pathlib import Path
from urllib.parse import quote_plus


def load_environment():
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:
        return

    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path)


def build_postgres_url():
    import os

    explicit_url = os.getenv("IOT_FUZZY_POSTGRES_URL") or os.getenv("IOT_FUZZY_DB_URL")
    if explicit_url:
        return explicit_url

    username = quote_plus(os.getenv("DB_USERNAME", "postgres"))
    password = quote_plus(os.getenv("DB_PASSWORD", "postgres"))
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "iot_fuzzy_kideco")

    return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
