import os
import pathlib
import datetime
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from google.auth.transport.requests import Request as GoogleRequest
from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

# Allow HTTP usage for local development
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# === Gerekli bilgiler ===
BASE_DIR = pathlib.Path(__file__).parent.resolve()
# Path to your client_secret.json file
CLIENT_SECRET_FILE = BASE_DIR / 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
# Redirect URI after OAuth2 authentication
REDIRECT_URI = 'http://localhost:8000/oauth2callback'
TOKEN_FILE = 'token.json'  # Token file to save the credentials after authentication
today = datetime.datetime.now()


async def oauth2callback(request: Request):
    # Initialize OAuth2 flow using the client secrets and required scopes
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRET_FILE),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    # Fetch the token from the authorization response
    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials

    # Save the credentials to token.json file for future use
    with open(TOKEN_FILE, "w") as token_file:
        token_file.write(credentials.to_json())

    return HTMLResponse("<h2>Auth is correct. You can now add events to your calendar!</h2>")

# Create the service to interact with the Google Calendar API


def create_service():
    creds = None
    # Load existing credentials from token.json if available
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If credentials are not available or expired, initiate the OAuth2 process
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            # Use the OAuth2 flow to get new credentials
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the new credentials to token.json for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    # Build the Google Calendar API service
    service = build('calendar', 'v3', credentials=creds)
    return service
