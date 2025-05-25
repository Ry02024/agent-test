import streamlit as st

def show():
    st.header("🏠 ホームページ")
    if "user_info" in st.session_state and st.session_state.user_info:
        user_name = st.session_state.user_info.get("name", "ユーザー")
        user_email = st.session_state.user_info.get("email")
        user_picture = st.session_state.user_info.get("picture")

        col1, col2 = st.columns([1, 5])
        with col1:
            if user_picture:
                st.image(user_picture, width=70)
        with col2:
            st.subheader(f"ようこそ、{user_name} さん！")
            st.write(f"メールアドレス: {user_email}")

        st.write("---")
        st.write("これはログイン後に表示されるメインコンテンツです。")
        # ここにアプリケーションの機能を追加
    else:
        # この状態はapp.pyで処理されるため、通常ここには到達しないはず
        st.warning("ログインしていません。")