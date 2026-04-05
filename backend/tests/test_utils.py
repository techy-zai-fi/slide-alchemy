import pytest
from pathlib import Path
from app.utils.encryption import encrypt_value, decrypt_value
from app.utils.config import ensure_data_dir, save_settings, load_settings, DATA_DIR
from app.models.settings import AppSettings, ModelProvider


def test_encrypt_decrypt_roundtrip():
    original = "secret-api-key-12345"
    encrypted = encrypt_value(original)
    assert encrypted != original
    decrypted = decrypt_value(encrypted)
    assert decrypted == original


def test_encrypt_produces_different_output():
    value = "test-value"
    enc1 = encrypt_value(value)
    enc2 = encrypt_value(value)
    # Fernet produces different ciphertext each time (different IV)
    assert enc1 != enc2


def test_ensure_data_dir_creates_dirs():
    ensure_data_dir()
    assert DATA_DIR.exists()
    assert (DATA_DIR / "projects").exists()


def test_save_and_load_settings():
    settings = AppSettings(
        active_provider=ModelProvider.GROQ,
        serper_api_key="test-serper-key",
    )
    save_settings(settings)
    loaded = load_settings()
    assert loaded.active_provider == ModelProvider.GROQ
    assert loaded.serper_api_key == "test-serper-key"


def test_load_settings_returns_default_when_no_config():
    from app.utils.config import CONFIG_FILE
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
    settings = load_settings()
    assert settings.active_provider == ModelProvider.OLLAMA
