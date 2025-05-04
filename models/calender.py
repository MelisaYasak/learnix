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

# Google Takvim etkinliklerini oluşturmak


def get_next_weekday_date(day_name, start_date):
    weekday_map = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }

    today_weekday = start_date.weekday()  # Bugünün haftanın günü numarasını al
    if day_name.lower() == 'today':
        target_weekday = today.weekday()
    target_weekday = weekday_map[day_name]  # Hedef haftanın gününü al

    # Eğer hedef gün bugün ya da sonraki bir günse
    days_diff = (target_weekday - today_weekday) % 7
    next_target_date = start_date + datetime.timedelta(days=days_diff)

    return next_target_date

# Google Takvim etkinliklerini oluşturmak


def convert_events_to_calendar(study_plan):
    event_list = []  # Etkinlikleri tutacağımız liste

    current_date = today  # Başlangıç tarihi
    for item in study_plan.schedule:
        print("****************************************************************************************************************************************")
        print(item)
        target_day = item.day  # Planlanan gün (örneğin 'Monday')
        event_start_time = item.start  # Başlangıç saati
        event_end_time = item.end  # Bitiş saati
        print(event_start_time)
        print(event_end_time)
        # Hedef günün tarihini bulalım
        target_date = get_next_weekday_date(target_day, current_date)

        # Etkinlik başlatma ve bitiş tarihlerini oluşturma
        start_time = datetime.datetime.combine(target_date, datetime.datetime.strptime(
            event_start_time, '%HH:%MM').time()).replace(tzinfo=datetime.timezone.utc)
        end_time = datetime.datetime.combine(target_date, datetime.datetime.strptime(
            event_end_time, '%HH:%MM').time()).replace(tzinfo=datetime.timezone.utc)

        # Etkinlik oluşturma
        event = {
            'summary': item['title'],
            'description': item['description'],
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
        }

        # Etkinliği listeye ekle
        event_list.append(event)

    return event_list


def create_service():
    if not os.path.exists("token.json"):
        return RedirectResponse("/")

    with open("token.json", "r") as token_file:
        creds_data = json.load(token_file)

    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    service = build("calendar", "v3", credentials=creds)
    return service
