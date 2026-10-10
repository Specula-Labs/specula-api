from app.config import Settings


def test_dotenv_overrides_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for key in ("ENVIRONMENT", "OPERATION_SCAN_LIMIT", "REQUEST_TIMEOUT_SECONDS"):
        monkeypatch.delenv(key, raising=False)
    (tmp_path / ".env").write_text(
        "ENVIRONMENT=offline-test\nOPERATION_SCAN_LIMIT=17\nREQUEST_TIMEOUT_SECONDS=2.5\n",
        encoding="utf-8",
    )
    settings = Settings()
    assert settings.environment == "offline-test"
    assert settings.operation_scan_limit == 17
    assert settings.request_timeout_seconds == 2.5


def test_environment_overrides_dotenv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("ENVIRONMENT=from-file\n", encoding="utf-8")
    monkeypatch.setenv("ENVIRONMENT", "from-environment")
    assert Settings().environment == "from-environment"
