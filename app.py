from fastapi import FastAPI, Request
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
import models.planner as p

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "")

    # Analyze the request and check if it's a study plan request
    analysis = await s.analyze_request(message)

    if analysis.get("is_study_plan_request", False):
        # Generate a study plan if requested
        response = await s.generate_schedule(message)
        # Create PlanResponse from the generated schedule
        p.set_study_plan(response)
    else:
        # Handle regular chat responses
        response = await s.generate_chat_response(message)

    return JSONResponse(content=response)


@app.post("/add-to-calendar")
async def add_to_calendar():
    created_events = []
    event_links = []
    schedule_list = p.get_study_plan()
    service = c.create_service()

    # Ensure the service is valid
    if not hasattr(service, 'events'):
        raise ValueError("Google Calendar service not properly initialized.")

    event_list = p.convert_events_to_calendar(schedule_list['content'])
    for event in event_list:
        created_event = service.events().insert(
            calendarId='primary', body=event).execute()
        event_links.append(created_event.get('htmlLink'))
        created_events.append(created_event)
        print(f"Event created: {created_event.get('htmlLink')}")

    # Return a response with links to all created events
    return {
        "message": f"{len(created_events)} event(s) created.",
        "event_links": event_links
    }
