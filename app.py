import streamlit as st
from src.my_streamlit_app import auth, config # 作成したモジュールをインポート
from src.my_streamlit_app.pages import home   # ホームページモジュールをインポート

def initialize_session_state():
    """セッションステートの初期化"""
    if "user_info" not in st.session_state:
        st.session_state["user_info"] = None
    if "auth_flow" not in st.session_state:
        st.session_state["auth_flow"] = {}

def handle_oauth_callback():
    """OAuthコールバックを処理し、ユーザー情報を取得・保存する"""
    query_params = st.query_params
    auth_code = query_params.get("code")
    received_csrf_state = query_params.get("state")

    if config.DEBUG_MODE:
        print(f"DEBUG (app.py - handle_oauth_callback start): auth_code='{auth_code}', received_csrf_state='{received_csrf_state}'")

    if config.DEBUG_MODE:
        print("--- OAuth Callback ---")
        print(f"Query Params: {dict(query_params)}") # dictに変換して表示
        print(f"Auth Code: {auth_code}")
        print(f"Received CSRF State: {received_csrf_state}")
    if auth_code and received_csrf_state:
        # auth_flowが初期化されていることを確認
        if config.DEBUG_MODE:
            print(f"DEBUG (app.py - handle_oauth_callback): Before auth_flow check. auth_flow: {st.session_state.get('auth_flow')}")
        if "auth_flow" not in st.session_state or not st.session_state.auth_flow:
             st.warning("認証フローが開始されていません。再度ログインをお試しください。")
             st.query_params.clear() # 不要なパラメータをクリア
             st.rerun()
             return
        
        if config.DEBUG_MODE:
            print(f"Expected CSRF State from session: {st.session_state['auth_flow'].get('oauth_state')}")

        try:
            user_info = auth.fetch_token_and_user_info(auth_code, received_csrf_state)
            st.session_state["user_info"] = user_info
            if config.DEBUG_MODE:
                print("User Info Fetched:", user_info)

            # 認証フロー関連のセッション情報をクリア
            if "auth_flow" in st.session_state:
                 del st.session_state["auth_flow"]
            st.query_params.clear()  # URLから認証コードとstateを削除
            st.rerun()  # ログイン状態を反映させるために再実行
        except ValueError as ve: # CSRFエラーや設定エラーなど
            if config.DEBUG_MODE: # DEBUG_MODEがTrueの時のみ出力
                print(f"DEBUG (app.py - except ValueError): Entered ValueError except block. Error: {ve}")
                # st.session_state.get の結果を直接確認
                auth_flow_value = st.session_state.get('auth_flow')
                print(f"DEBUG (app.py - except ValueError): Value of st.session_state.get('auth_flow'): {auth_flow_value}")
                # For more detailed inspection of the mocked session state, you might need to access its internal dict if possible,
                # but st.session_state.get() should be the primary way to check.
                # イテレーション中に変更される可能性を避けるため、キーのリストを先に作成
                keys_in_session = list(st.session_state.keys())
                print(f"DEBUG (app.py - except ValueError): Keys in st.session_state (before del check): {keys_in_session}")
            st.error(f"認証エラー: {ve}")
            if "auth_flow" in st.session_state:
                if config.DEBUG_MODE:
                    print(f"DEBUG (app.py - except ValueError): 'auth_flow' found in session. Attempting to delete.")
                del st.session_state["auth_flow"]
            st.experimental_set_query_params()
            # st.rerun() # エラー表示後、ログインページに戻すために再実行も検討
        except Exception as e:
            st.error(f"ログイン処理中に予期せぬエラーが発生しました: {e}")
            if "auth_flow" in st.session_state:
                 del st.session_state["auth_flow"]
            st.query_params.clear()
            # st.rerun()

def main():
    initialize_session_state()
    if config.DEBUG_MODE:
        print("--- Session State Initialized ---")
        print("User Info:", st.session_state["user_info"])
        print("Auth Flow:", st.session_state["auth_flow"])

    handle_oauth_callback() # 毎回コールバックをチェック

    if st.session_state["user_info"]:
        # ログイン済みの場合
        if st.sidebar.button("ログアウト", key="logout_button_main"):
            auth.logout()
            st.rerun() # ログアウト後にページを再読み込み
        if config.DEBUG_MODE:
            print("--- Logged In User ---")
            print("User Info:", st.session_state["user_info"])
        home.show()  # ホームページ表示
    else:
        # 未ログインの場合
        st.title("Streamlit アプリへようこそ")
        st.write("Googleアカウントでログインしてください。")
        auth_url = auth.get_google_auth_url()
        if auth_url:
            # st.markdown(f'<a href="{auth_url}" target="_self" class="button">Googleでログイン</a>', unsafe_allow_html=True)
            # st.buttonの代わりにst.link_buttonを使用 (Streamlit 1.28.0+)
            st.link_button("Googleでログイン", auth_url, use_container_width=True)
        else:
            st.error("ログインURLの生成に失敗しました。設定を確認してください。")

if __name__ == "__main__":
    main()