from __future__ import print_function

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDS_PATH = "credentials.json"
TOKEN_PATH = "token.json"

def main():
    creds = None

    # 既存token.jsonの読み込み
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # 有効期限切れ → 更新
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # 認証フロー
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)

        # token.json に保存
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    print("認証完了！token.json を作成しました。")

if __name__ == '__main__':
    main()
