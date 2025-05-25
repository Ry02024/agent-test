import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む (プロジェクトルートの.envを参照)
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not REDIRECT_URI:
    # 実際のアプリケーションでは、ここでエラーを発生させるか、
    # Streamlitのst.error()でユーザーに設定が不足していることを通知することを検討してください。
    print("警告: Google OAuthの環境変数が設定されていません。(.envファイルを確認してください)")

AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo" # ユーザー情報を取得するためのURL
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",  # ユーザーのメールアドレスへのアクセス
    "https://www.googleapis.com/auth/userinfo.profile", # ユーザーの基本的なプロフィール情報へのアクセス
    "openid"  # OpenID Connectのスコープ (IDトークン取得に必要)
]