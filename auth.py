import sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_auth_url():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    flow.redirect_uri = "http://localhost"
    auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent")
    print(auth_url)


def save_token(auth_response_url):
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    flow.redirect_uri = "http://localhost"
    flow.fetch_token(authorization_response=auth_response_url)
    with open("token.json", "w") as f:
        f.write(flow.credentials.to_json())
    print("token.json saved successfully!")


if len(sys.argv) == 2:
    save_token(sys.argv[1])
else:
    get_auth_url()
