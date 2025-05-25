import pytest
from unittest.mock import patch, MagicMock
import secrets

# Mock streamlit and config before importing auth
@pytest.fixture(autouse=True)
def mock_streamlit_and_config():
    """Mocks streamlit and config modules for auth tests."""
    with patch.dict('sys.modules', {
        'streamlit': MagicMock(),
        'src.my_streamlit_app.config': MagicMock()
    }) as sys_modules:
        # Import streamlit after mocking
        import streamlit as st
        # Setup mock for st.session_state
        st.session_state = MagicMock()
        st.session_state.auth_flow = {} # Initialize auth_flow

        # Setup mock for config module
        config_mock = sys_modules['src.my_streamlit_app.config']
        config_mock.GOOGLE_CLIENT_ID = "test_client_id"
        config_mock.GOOGLE_CLIENT_SECRET = "test_client_secret"
        config_mock.REDIRECT_URI = "http://localhost:8501"
        config_mock.SCOPES = ["openid", "email", "profile"]
        config_mock.AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
        config_mock.TOKEN_URL = "https://oauth2.googleapis.com/token"
        config_mock.USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
        config_mock.DEBUG_MODE = False # Default to False for tests unless overridden
        yield st, config_mock


@pytest.fixture
def auth_module():
    """Fixture to import the auth module after mocks are set up."""
    from src.my_streamlit_app import auth
    return auth


def test_get_google_auth_url(mock_streamlit_and_config, auth_module):
    """Test generation of Google authentication URL."""
    st_mock, config_mock = mock_streamlit_and_config

    with patch('src.my_streamlit_app.auth.OAuth2Session') as mock_oauth_session: # パッチのターゲットを修正
        mock_session_instance = mock_oauth_session.return_value
        mock_session_instance.authorization_url.return_value = ("http://auth_url", "test_state")

        auth_url = auth_module.get_google_auth_url()

        assert auth_url == "http://auth_url"
        mock_oauth_session.assert_called_once_with(
            config_mock.GOOGLE_CLIENT_ID,
            scope=config_mock.SCOPES,
            redirect_uri=config_mock.REDIRECT_URI,
            state=st_mock.session_state.auth_flow["oauth_state"] # Check if state was set
        )
        mock_session_instance.authorization_url.assert_called_once_with(
            config_mock.AUTHORIZATION_URL,
            access_type="offline",
            prompt="consent"
        )
        assert "oauth_state" in st_mock.session_state.auth_flow
        assert len(st_mock.session_state.auth_flow["oauth_state"]) > 10 # Check if state is a reasonable string

def test_get_google_auth_url_no_client_id(mock_streamlit_and_config, auth_module):
    """Test get_google_auth_url when GOOGLE_CLIENT_ID is not set."""
    st_mock, config_mock = mock_streamlit_and_config
    config_mock.GOOGLE_CLIENT_ID = None

    auth_url = auth_module.get_google_auth_url()

    assert auth_url is None
    st_mock.error.assert_called_once_with("Google Client IDが設定されていません。管理者にお問い合わせください。")


def test_fetch_token_and_user_info_success(mock_streamlit_and_config, auth_module):
    """Test successful fetching of token and user info."""
    st_mock, config_mock = mock_streamlit_and_config
    csrf_state = secrets.token_urlsafe(16)
    st_mock.session_state.auth_flow = {"oauth_state": csrf_state}
    authorization_code = "test_auth_code"

    with patch('src.my_streamlit_app.auth.OAuth2Session') as mock_oauth_session: # パッチのターゲットを修正
        mock_session_instance = mock_oauth_session.return_value
        mock_session_instance.fetch_token.return_value = {
            "access_token": "test_access_token",
            "id_token": "test_id_token"
        }
        mock_user_info_response = MagicMock()
        mock_user_info_response.json.return_value = {
            "email": "test@example.com",
            "name": "Test User",
            "picture": "http://picture_url"
        }
        mock_session_instance.get.return_value = mock_user_info_response

        user_data = auth_module.fetch_token_and_user_info(authorization_code, csrf_state)

        assert user_data["email"] == "test@example.com"
        assert user_data["name"] == "Test User"
        assert user_data["picture"] == "http://picture_url"
        assert user_data["access_token"] == "test_access_token"
        mock_session_instance.fetch_token.assert_called_once()
        mock_session_instance.get.assert_called_once_with(config_mock.USERINFO_URL)

def test_fetch_token_and_user_info_csrf_mismatch(mock_streamlit_and_config, auth_module):
    """Test fetch_token_and_user_info with CSRF state mismatch."""
    st_mock, _ = mock_streamlit_and_config
    st_mock.session_state.auth_flow = {"oauth_state": "expected_csrf_state"}

    with pytest.raises(ValueError, match="CSRF state mismatch"):
        auth_module.fetch_token_and_user_info("test_auth_code", "received_wrong_csrf_state")
    st_mock.error.assert_called_with("CSRFトークンが無効です。ログインをやり直してください。")

def test_fetch_token_and_user_info_no_config(mock_streamlit_and_config, auth_module):
    """Test fetch_token_and_user_info when OAuth config is incomplete."""
    st_mock, config_mock = mock_streamlit_and_config
    config_mock.GOOGLE_CLIENT_SECRET = None # Simulate incomplete config

    with pytest.raises(ValueError, match="OAuth設定が不完全です。"):
        auth_module.fetch_token_and_user_info("test_auth_code", "any_csrf_state")
    st_mock.error.assert_called_with("Google Client IDまたはSecretが設定されていません。")


def test_logout(mock_streamlit_and_config, auth_module):
    """Test logout functionality."""
    st_mock, _ = mock_streamlit_and_config
    st_mock.session_state.user_info = {"name": "Test User"}
    st_mock.session_state.auth_flow = {"oauth_state": "some_state"}

    auth_module.logout()

    assert "user_info" not in st_mock.session_state
    assert "auth_flow" not in st_mock.session_state
    st_mock.query_params.clear.assert_called_once()
    st_mock.success.assert_called_once_with("ログアウトしました。")