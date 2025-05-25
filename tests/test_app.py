import pytest
from unittest.mock import patch, MagicMock

# Mock streamlit, config, auth, and pages.home before importing app
@pytest.fixture(autouse=True)
def mock_dependencies():
    """Mocks streamlit and other app dependencies."""
    mock_st = MagicMock()

    # st.session_state をより堅牢にモックするための内部辞書を mock_st の属性として持つ
    mock_st._internal_session_dict = {}

    def _session_get(key, default=None):
        # print(f"DEBUG (_session_get): key='{key}', dict={mock_st._internal_session_dict}")
        return mock_st._internal_session_dict.get(key, default)
    
    def _session_set(key, value):
        mock_st._internal_session_dict[key] = value
        return value

    def _session_contains(key):
        # print(f"DEBUG (_session_contains): key='{key}', dict={mock_st._internal_session_dict}")
        return key in mock_st._internal_session_dict

    def _session_del(key):
        # print(f"DEBUG (_session_del): key='{key}', dict before del={mock_st._internal_session_dict}")
        if key in mock_st._internal_session_dict:
            del mock_st._internal_session_dict[key]
        # print(f"DEBUG (_session_del): dict after del={mock_st._internal_session_dict}")
    
    def _session_clear():
        mock_st._internal_session_dict.clear()

    mock_st.session_state = MagicMock()
    mock_st.session_state.get = MagicMock(side_effect=_session_get)
    mock_st.session_state.__setitem__ = MagicMock(side_effect=_session_set)
    mock_st.session_state.__getitem__ = MagicMock(side_effect=lambda k: mock_st._internal_session_dict[k])
    mock_st.session_state.__contains__ = MagicMock(side_effect=_session_contains)
    mock_st.session_state.__delitem__ = MagicMock(side_effect=_session_del)
    mock_st.session_state.keys = MagicMock(return_value=mock_st._internal_session_dict.keys()) # keys()メソッドをモック
    mock_st.session_state.__iter__ = MagicMock(return_value=iter(mock_st._internal_session_dict))
    mock_st.session_state.clear = MagicMock(side_effect=_session_clear)

    # フィクスチャの開始時に常にクリーンな状態にする
    mock_st._internal_session_dict.clear()
    mock_st._internal_session_dict["user_info"] = None
    mock_st._internal_session_dict["auth_flow"] = {}

    mock_st.query_params = MagicMock()
    # デフォルトではクエリパラメータは存在しない (Noneを返す) ようにする
    mock_st.query_params.get = MagicMock(return_value=None)
    mock_st.query_params.clear = MagicMock()
    # experimental_set_query_params もモックしておく
    mock_st.experimental_set_query_params = MagicMock()


    mock_config = MagicMock()
    mock_config.DEBUG_MODE = False # Default for tests

    mock_auth = MagicMock()
    mock_pages_home = MagicMock()

    # streamlit.rerun のモック
    mock_st.rerun = MagicMock()


    with patch.dict('sys.modules', {
        'streamlit': mock_st,
        'src.my_streamlit_app.config': mock_config,
        'src.my_streamlit_app.auth': mock_auth,
        'src.my_streamlit_app.pages.home': mock_pages_home,
    }):
        yield mock_st, mock_config, mock_auth, mock_pages_home

@pytest.fixture
def app_module(mock_dependencies):
    """Fixture to import the app module after mocks are set up."""
    from app import initialize_session_state, handle_oauth_callback, main
    return initialize_session_state, handle_oauth_callback, main


def test_initialize_session_state(mock_dependencies, app_module):
    """Test session state initialization."""
    st_mock, _, _, _ = mock_dependencies
    initialize_session_state_func, _, _ = app_module

    # 1. 初期状態での呼び出し
    st_mock.session_state.clear() 

    initialize_session_state_func()
    assert st_mock.session_state["user_info"] is None
    assert st_mock.session_state["auth_flow"] == {}

    # 2. 既に値が設定されている場合の呼び出し（上書きされないことの確認）
    st_mock.session_state["user_info"] = {"name": "Test"}
    st_mock.session_state["auth_flow"] = {"state": "abc"}

    initialize_session_state_func() 

    assert st_mock.session_state["user_info"] == {"name": "Test"}
    assert st_mock.session_state["auth_flow"] == {"state": "abc"}


def test_handle_oauth_callback_no_code(mock_dependencies, app_module):
    """Test OAuth callback when no auth code is present."""
    st_mock, _, _, _ = mock_dependencies
    _, handle_oauth_callback_func, _ = app_module

    def query_params_get_side_effect(key):
        if key == "code":
            return None
        elif key == "state":
            return "some_state"
        return None
    st_mock.query_params.get.side_effect = query_params_get_side_effect

    handle_oauth_callback_func()
    assert st_mock.session_state["user_info"] is None
    # auth.fetch_token_and_user_info が呼ばれないことを確認 (間接的に)
    # st.error や st.rerun が呼ばれないことも確認できるが、ここでは user_info の状態を主眼に置く


def test_handle_oauth_callback_success(mock_dependencies, app_module):
    """Test successful OAuth callback and user info fetching."""
    st_mock, config_mock, auth_mock, _ = mock_dependencies
    _, handle_oauth_callback_func, _ = app_module
    config_mock.DEBUG_MODE = True # デバッグプリントを有効にする場合

    def query_params_get_side_effect(key):
        if key == "code":
            return "test_code"
        elif key == "state":
            return "test_csrf_state"
        return None
    st_mock.query_params.get.side_effect = query_params_get_side_effect
    
    st_mock.session_state.clear()
    st_mock.session_state["auth_flow"] = {"oauth_state": "test_csrf_state"}
    auth_mock.fetch_token_and_user_info.return_value = {"name": "Test User", "email": "test@example.com"}

    handle_oauth_callback_func()

    auth_mock.fetch_token_and_user_info.assert_called_once_with("test_code", "test_csrf_state")
    assert st_mock.session_state["user_info"] == {"name": "Test User", "email": "test@example.com"}
    assert "auth_flow" not in st_mock._internal_session_dict 
    st_mock.query_params.clear.assert_called_once()
    st_mock.rerun.assert_called_once()


def test_handle_oauth_callback_csrf_error(mock_dependencies, app_module):
    st_mock, config_mock, auth_mock, _ = mock_dependencies 
    _, handle_oauth_callback_func, _ = app_module 
    config_mock.DEBUG_MODE = True 

    def query_params_get_side_effect(key):
        if key == "code":
            return "test_code" 
        elif key == "state":
            return "received_wrong_csrf_state" # 期待されるstateとは異なるstate
        return None
    st_mock.query_params.get.side_effect = query_params_get_side_effect

    st_mock.session_state.clear()
    st_mock.session_state["auth_flow"] = {"oauth_state": "expected_csrf_state"} # app.py側の期待値
    # fetch_token_and_user_info が ValueError を発生させるようにモック
    # auth.py側のCSRFチェックでエラーを発生させるか、app.py側のエラーハンドリングをテストするかで戦略が分かれる
    # ここでは app.py 側の except ValueError をテストするため、auth.py 側でエラーが発生したと仮定
    auth_mock.fetch_token_and_user_info.side_effect = ValueError("CSRF state mismatch from auth.py")

    handle_oauth_callback_func()

    st_mock.error.assert_called_with("認証エラー: CSRF state mismatch from auth.py")
    # __delitem__ が "auth_flow" で呼ばれたか確認
    st_mock.session_state.__delitem__.assert_called_with("auth_flow")
    assert "auth_flow" not in st_mock._internal_session_dict
    # app.py の except ValueError ブロックでは st.query_params.clear() の代わりに st.experimental_set_query_params() を呼んでいるので修正
    st_mock.experimental_set_query_params.assert_called_once_with() 
    st_mock.rerun.assert_not_called()

def test_main_not_logged_in(mock_dependencies, app_module):
    """Test main function when user is not logged in."""
    st_mock, config_mock, auth_mock, _ = mock_dependencies # config_mock を受け取る
    _, _, main_func = app_module # main関数のみ取得

    config_mock.DEBUG_MODE = True # デバッグプリントを有効化
    st_mock.session_state.clear()
    st_mock.session_state["user_info"] = None
    auth_mock.get_google_auth_url.return_value = "http://google_auth_url"

    # test_main_not_logged_in の main_func() 呼び出し前
    print(f"DEBUG (test_main_not_logged_in): st_mock.query_params.get.return_value = {st_mock.query_params.get.return_value}")
    print(f"DEBUG (test_main_not_logged_in): auth_mock.fetch_token_and_user_info.return_value = {auth_mock.fetch_token_and_user_info.return_value}")
    main_func()

    st_mock.title.assert_called_with("Streamlit アプリへようこそ")
    auth_mock.get_google_auth_url.assert_called_once()
    st_mock.link_button.assert_called_with("Googleでログイン", "http://google_auth_url", use_container_width=True)


def test_main_logged_in(mock_dependencies, app_module):
    """Test main function when user is logged in."""
    st_mock, config_mock, auth_mock, home_mock = mock_dependencies # config_mock を受け取る
    _, _, main_func = app_module

    config_mock.DEBUG_MODE = True # デバッグプリントを有効化
    st_mock.session_state.clear()
    st_mock.session_state["user_info"] = {"name": "Test User", "email": "test@example.com"}
    st_mock.sidebar.button.return_value = False 

    main_func()

    home_mock.show.assert_called_once()
    st_mock.sidebar.button.assert_called_with("ログアウト", key="logout_button_main")
    auth_mock.logout.assert_not_called() 

def test_main_logged_in_and_logout(mock_dependencies, app_module):
    """Test main function when user is logged in and clicks logout."""
    st_mock, config_mock, auth_mock, home_mock = mock_dependencies # config_mock を受け取る
    _, _, main_func = app_module

    config_mock.DEBUG_MODE = True # デバッグプリントを有効化
    st_mock.session_state.clear()
    st_mock.session_state["user_info"] = {"name": "Test User", "email": "test@example.com"}
    st_mock.sidebar.button.return_value = True 
    st_mock.rerun.side_effect = StopIteration 

    print(f"DEBUG (test_main_logged_in_and_logout): st_mock.query_params.get.return_value = {st_mock.query_params.get.return_value}")
    print(f"DEBUG (test_main_logged_in_and_logout): auth_mock.fetch_token_and_user_info.return_value = {auth_mock.fetch_token_and_user_info.return_value}")
    with pytest.raises(StopIteration):
        main_func()

    auth_mock.logout.assert_called_once()
    st_mock.rerun.assert_called_once() 
    home_mock.show.assert_not_called() 
    st_mock.rerun.side_effect = None