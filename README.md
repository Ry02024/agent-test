# 初めてのStreamlitアプリ

これはStreamlitで構築された、Google OAuth 2.0による認証機能を備えたアプリケーションです。Pythonのバージョン管理にpyenvを、依存関係管理にPoetryを使用し、`src`ディレクトリを中心とした構造化されたアプローチでStreamlitアプリをセットアップして実行する方法の基本的な例として機能します。

## プロジェクト構造

このプロジェクトの主なファイルとディレクトリは次のとおりです。

```
.
├── .env                  # 環境変数（.gitignoreで保護）
├── .gitignore            # Gitで無視するファイルを指定
├── .python-version       # pyenvで使用するPythonバージョン
├── README.md             # このファイル
├── app.py                # Streamlitアプリケーションのメインエントリポイント
├── index.html            # (オプションの静的ファイル、この例では未使用)
├── poetry.lock           # 依存関係のロックファイル
├── pyproject.toml        # Poetryのプロジェクト設定と依存関係
└── src/                  # アプリケーションの主要なソースコード
    └── my_streamlit_app/ # メインのPythonパッケージ
        ├── __init__.py
        ├── auth.py       # 認証関連のロジック
        ├── config.py     # 設定情報（APIキーなど）
        └── pages/        # Streamlitのマルチページ機能のページ
            ├── __init__.py
            ├── .keep       # ディレクトリ構造維持のためのダミーファイル
            └── home.py     # ホームページ
```

主要なアプリケーションロジックは`src/my_streamlit_app/`ディレクトリ内に配置されます。`app.py`は、これらのモジュールを呼び出してアプリケーションを起動する役割を担います。

## 認証機能

このアプリケーションは、ユーザー認証のためにGoogle OAuth 2.0を使用しています。これにより、ユーザーは自身のGoogleアカウントを使用して安全にログインできます。アプリケーションはユーザーのメールアドレス、名前、プロフィール画像を取得し、パーソナライズされた体験を提供します。

## セットアップ手順

### 必要な環境変数

このアプリケーションをローカルで実行するには、Google OAuth 2.0の認証情報を含む環境変数を設定する必要があります。プロジェクトのルートディレクトリに`.env`という名前のファイルを作成し、以下の形式で必要な情報を記述してください。

```env
GOOGLE_CLIENT_ID="YOUR_GOOGLE_CLIENT_ID_HERE"
GOOGLE_CLIENT_SECRET="YOUR_GOOGLE_CLIENT_SECRET_HERE"
REDIRECT_URI="YOUR_REDIRECT_URI_HERE"
```

**各変数の説明:**

*   `GOOGLE_CLIENT_ID`: Google Cloud Consoleで取得したOAuth 2.0クライアントIDです。
*   `GOOGLE_CLIENT_SECRET`: Google Cloud Consoleで取得したクライアントシークレットです。
*   `REDIRECT_URI`: Google OAuth 2.0で承認されたリダイレクトURIです。ローカル開発の場合、通常は `http://localhost:8501` のようなStreamlitアプリが動作するURLになります。Google Cloud ConsoleでこのURIを事前に登録しておく必要があります。

これらの認証情報は、Google Cloud Console ([https://console.cloud.google.com/](https://console.cloud.google.com/)) の「APIとサービス」>「認証情報」セクションで、OAuth 2.0クライアントIDを作成または選択することで取得できます。

**重要:** `.env`ファイルには機密情報が含まれるため、Gitリポジトリにはコミットしないでください。このプロジェクトの`.gitignore`ファイルには、`.env`ファイルが既に記載されており、誤ってコミットされるのを防ぎます。

### 1. Python環境のセットアップ (pyenv & Python 3.11)

Pythonのバージョンを管理するには`pyenv`を使用することをお勧めします。

**pyenvのインストール:**

`pyenv`がインストールされていない場合は、公式の手順に従ってインストールできます。一般的な方法は次のとおりです。
```bash
curl https://pyenv.run | bash
```
インストール後、シェルの起動設定ファイルに`pyenv`を追加する必要があります。bashの場合、これは通常、`~/.bashrc`または`~/.zshrc`（zshを使用している場合）に次の行を追加することを意味します。

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
```
変更を有効にするには、シェルを再起動するか、設定ファイルをsourceしてください。

**Python 3.11.0のインストール:**

`pyenv`のセットアップが完了したら、Python 3.11.0をインストールします。
```bash
pyenv install 3.11.0
```

**ローカルPythonバージョンの設定:**

プロジェクトのルートディレクトリで、このプロジェクトのローカルPythonバージョンを設定します。
```bash
pyenv local 3.11.0
```
Pythonのバージョンを確認します。
```bash
python --version
# Python 3.11.0 と出力されるはずです
```

### 2. Poetryのインストール

依存関係の管理にはPoetryを使用します。インストールされていない場合は、次のようにしてインストールできます。
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
PoetryのbinディレクトリをPATHに追加する必要がある場合があります。インストーラーは通常、これに関する指示を提供します。例：
```bash
export PATH="/root/.local/bin:$PATH" # ホームディレクトリが異なる場合はパスを調整してください
```
Poetryのインストールを確認します。
```bash
poetry --version
```

### 3. 依存関係のインストール

Poetryと正しいPythonバージョンがセットアップされたら、プロジェクトのルートディレクトリでプロジェクトの依存関係をインストールします。
```bash
poetry install
```
このコマンドは、仮想環境が存在しない場合は作成し、`pyproject.toml`および`poetry.lock`にリストされているすべての依存関係をインストールします。

## Streamlitアプリの実行

依存関係をインストールし、`.env`ファイルに必要な環境変数を設定した後、Streamlitアプリケーションを実行できます。

1.  **仮想環境をアクティブにする（まだアクティブでない場合）：**
    Poetryコマンドは通常、プロジェクトの仮想環境内で自動的に実行されます。他の目的で手動でアクティブにする必要がある場合：
    ```bash
    poetry shell
    ```
    または、各コマンドの前に`poetry run`を付けます。

2.  **Streamlitアプリの実行：**
    プロジェクトのルートディレクトリから：
    ```bash
    poetry run streamlit run app.py
    ```

これによりStreamlit開発サーバーが起動し、デフォルトのWebブラウザが自動的にアプリのURL（通常は `http://localhost:8501`）を開きます。ログインページが表示され、Googleアカウントでログインするとホームページにアクセスできます。
(注: `app.py`はGoogle OAuthログインフローを処理し、成功すると`src/my_streamlit_app/pages/home.py`のコンテンツを表示します。)
