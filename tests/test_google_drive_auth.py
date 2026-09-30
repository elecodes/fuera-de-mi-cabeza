from unittest.mock import MagicMock, patch

import pytest

from app.services.google_drive_auth import build_drive_service


def test_build_drive_service_raises_without_token_file():
    with pytest.raises(RuntimeError, match="GOOGLE_OAUTH_TOKEN_FILE"):
        build_drive_service(None)


def test_build_drive_service_raises_when_token_file_missing(tmp_path):
    missing = tmp_path / "no-existe.json"
    with pytest.raises(RuntimeError, match="No se encontró el archivo de autorización"):
        build_drive_service(str(missing))


def test_build_drive_service_returns_service_for_valid_token(tmp_path):
    token_file = tmp_path / "token.json"
    token_file.write_text("{}", encoding="utf-8")

    fake_creds = MagicMock()
    fake_creds.valid = True
    fake_service = object()

    with patch("app.services.google_drive_auth.Credentials.from_authorized_user_file", return_value=fake_creds), \
         patch("app.services.google_drive_auth.build", return_value=fake_service) as mock_build:
        service = build_drive_service(str(token_file))

    assert service is fake_service
    mock_build.assert_called_once()


def test_build_drive_service_refreshes_and_persists_expired_token(tmp_path):
    token_file = tmp_path / "token.json"
    token_file.write_text("{}", encoding="utf-8")

    fake_creds = MagicMock()
    fake_creds.valid = False
    fake_creds.expired = True
    fake_creds.refresh_token = "a-refresh-token"
    fake_creds.to_json.return_value = '{"renewed": true}'

    def fake_refresh(request):
        fake_creds.valid = True

    fake_creds.refresh.side_effect = fake_refresh

    with patch("app.services.google_drive_auth.Credentials.from_authorized_user_file", return_value=fake_creds), \
         patch("app.services.google_drive_auth.build", return_value=object()):
        build_drive_service(str(token_file))

    fake_creds.refresh.assert_called_once()
    assert token_file.read_text(encoding="utf-8") == '{"renewed": true}'


def test_build_drive_service_raises_when_expired_without_refresh_token(tmp_path):
    token_file = tmp_path / "token.json"
    token_file.write_text("{}", encoding="utf-8")

    fake_creds = MagicMock()
    fake_creds.valid = False
    fake_creds.expired = True
    fake_creds.refresh_token = None

    with patch("app.services.google_drive_auth.Credentials.from_authorized_user_file", return_value=fake_creds):
        with pytest.raises(RuntimeError, match="no tiene refresh token"):
            build_drive_service(str(token_file))
