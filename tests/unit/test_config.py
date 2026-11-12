from dia.core.config import Settings


def test_default_settings():
    settings = Settings(_env_file=None)

    assert settings.app_name == "document-intelligence-api"
    assert settings.app_version == "0.1.0"
    assert settings.app_env == "development"


def test_custom_settings():
    settings = Settings(
        _env_file=None,
        app_name="Test Document API",
        app_env="testing",
        debug=True,
    )

    assert settings.app_name == "Test Document API"
    assert settings.app_env == "testing"
    assert settings.debug is True


def test_api_prefix():
    settings = Settings(
        _env_file=None,
        api_v1_prefix="/custom/v1",
    )

    assert settings.api_v1_prefix == "/custom/v1"
