from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import pathlib
import json

import models.scheduler as s
import models.calender as c


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # http:// kullanımına izin ver

# === Gerekli bilgiler ===
BASE_DIR = pathlib.Path(__file__).parent.resolve()
CLIENT_SECRET_FILE = BASE_DIR / 'models/client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
# BU URI Google Console'da da kayıtlı olmalı
REDIRECT_URI = 'http://localhost:8000/oauth2callback'


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    flow = Flow.from_client_secrets_file(
        str(CLIENT_SECRET_FILE),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    RedirectResponse(auth_url)

    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "")

    # First analyze if the user is requesting a study plan
    analysis = await s.analyze_request(message)

    if analysis.get("is_study_plan_request", False):
        # User is requesting a study plan
        response = await s.generate_schedule(message)
    else:
        # User is just chatting
        response = await s. generate_chat_response(message)
    return JSONResponse(content=response)


# Çalışma planı için model
class ScheduleItem(BaseModel):
    day: str
    start: str
    end: str
    title: str
    description: str


class PlanRequest(BaseModel):
    schedule: List[ScheduleItem]

# Takvime ekleme endpoint'i


@app.post("/add-to-calendar")
async def add_to_calendar(plan: PlanRequest):
    # Takvime etkinlik ekle
    service = c.create_service()

    event_list = c.convert_events_to_calendar(plan)
    for event in event_list:
        print("hello")
        '''created_event = service.events().insert(
            calendarId='primary', body=event).execute()
        print(f"Event created: {created_event.get('htmlLink')}")'''
    print(f"Plan Received: {plan.schedule}")
    return {
        "message": "Etkinlik oluşturuldu!",
    }


'''return {
    "message": "Etkinlik oluşturuldu!",
    "event_link": created_event.get('htmlLink')
}'''
