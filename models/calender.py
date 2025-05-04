from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import datetime
import os
import pathlib
import json
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # http:// kullanımına izin ver

# === Gerekli bilgiler ===
BASE_DIR = pathlib.Path(__file__).parent.resolve()
CLIENT_SECRET_FILE = BASE_DIR / 'models/client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
# BU URI Google Console'da da kayıtlı olmalı
REDIRECT_URI = 'http://localhost:8000/oauth2callback'
today = datetime.datetime.now()


def oauth2callback(request: Request):
    flow = Flow.from_client_secrets_file(
        str(CLIENT_SECRET_FILE),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials

    # token.json dosyasına kaydet
    with open("token.json", "w") as token_file:
        token_file.write(credentials.to_json())

    return HTMLResponse("<h2>Yetkilendirme başarılı! Artık takvime etkinlik ekleyebilirsiniz.</h2>")


def create_service():
    if not os.path.exists("token.json"):
        return RedirectResponse("/")

    with open("token.json", "r") as token_file:
        creds_data = json.load(token_file)

    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    service = build("calendar", "v3", credentials=creds)
    return service
