import streamlit as st
from requests_oauthlib import OAuth2Session
import secrets # CSRF対策用のランダムなstateを生成するため
from . import config # ローカルのconfigモジュールをインポート

def get_google_auth_url():
    """Googleの認証URLを生成し、CSRF対策用のstateをセッションに保存します。"""
    if not config.GOOGLE_CLIENT_ID:
        st.error("Google Client IDが設定されていません。管理者にお問い合わせください。")
        return None

    # CSRF対策のためのstateを生成
    csrf_state = secrets.token_urlsafe(16)
    if "auth_flow" not in st.session_state:
        st.session_state.auth_flow = {}
    st.session_state.auth_flow["oauth_state"] = csrf_state

    google = OAuth2Session(
        config.GOOGLE_CLIENT_ID,
        scope=config.SCOPES,
        redirect_uri=config.REDIRECT_URI,
        state=csrf_state # 生成したstateを渡す
    )
    authorization_url, state = google.authorization_url(
        config.AUTHORIZATION_URL,
        access_type="offline",  # リフレッシュトークンが必要な場合
        prompt="consent"        # 常に同意画面を表示させる（開発中は便利）
    )
    return authorization_url

def fetch_token_and_user_info(authorization_code: str, received_csrf_state: str):
    if not config.GOOGLE_CLIENT_ID or not config.GOOGLE_CLIENT_SECRET:
        st.error("Google Client IDまたはSecretが設定されていません。")
        raise ValueError("OAuth設定が不完全です。")

    if config.DEBUG_MODE: # DEBUG_MODEがTrueの時のみ出力
        print(f"DEBUG (auth.py - fetch_token): auth_flow before CSRF check: {st.session_state.get('auth_flow')}")

    # CSRF stateの検証
    expected_csrf_state = st.session_state.auth_flow.get("oauth_state")
    if not expected_csrf_state or expected_csrf_state != received_csrf_state:
        st.error("CSRFトークンが無効です。ログインをやり直してください。")
        raise ValueError("CSRF state mismatch")

    google = OAuth2Session(
        config.GOOGLE_CLIENT_ID,
        redirect_uri=config.REDIRECT_URI,
        state=expected_csrf_state
    )
    try:
        token = google.fetch_token(
            config.TOKEN_URL,
            client_secret=config.GOOGLE_CLIENT_SECRET,
            code=authorization_code
        )
    except Exception as e:
        st.error(f"トークンの取得に失敗しました: {e}")
        raise

    try:
        user_info_response = google.get(config.USERINFO_URL)
        user_info_response.raise_for_status()
        user_info = user_info_response.json()
    except Exception as e:
        st.error(f"ユーザー情報の取得に失敗しました: {e}")
        raise

    return {
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
        "id_token": token.get("id_token"),
        "access_token": token.get("access_token")
    }

def logout():
    """ユーザーをログアウトさせ、セッション情報をクリアします。"""
    keys_to_clear = ["user_info", "auth_flow"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.query_params.clear()
    st.success("ログアウトしました。")