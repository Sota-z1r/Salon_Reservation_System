from app import create_app
import os
import json

# credentials.json を書き出す
cred_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
if cred_json:
    with open("credentials.json", "w") as f:
        f.write(cred_json)

# token.json を書き出す
token_json = os.environ.get("GOOGLE_TOKEN_JSON")
if token_json:
    with open("token.json", "w") as f:
        f.write(token_json)


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
