# src/my_streamlit_app/pages/home.py
import streamlit as st

def show():
    st.header("🏠 ホームページ")
    if "user_info" in st.session_state and st.session_state.user_info:
        # デバッグ用にセッション情報をブラウザにも表示してみる（確認後削除）
        # st.write("ブラウザデバッグ (user_info):", st.session_state.user_info)

        user_name = st.session_state.user_info.get("name", "ユーザー") # "name" キーで取得
        user_email = st.session_state.user_info.get("email")
        user_picture = st.session_state.user_info.get("picture")

        col1, col2 = st.columns([1, 5])
        with col1:
            if user_picture:
                st.image(user_picture, width=70)
        with col2:
            st.subheader(f"ようこそ、{user_name} さん！") # ここで表示
            st.write(f"メールアドレス: {user_email}")

        st.write("---")
        st.write("これはログイン後に表示されるメインコンテンツです。")
    else:
        st.warning("ログインしていません。ホームページを表示できません。") # 通常ここには来ないはず
