from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import pathlib
import json

import models.scheduler as s
import models.planner as p

# Initialize FastAPI app
app = FastAPI()

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Home route
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Chat route: handles chat messages and study plan requests
@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "")

    # Analyze the message
    analysis = await s.analyze_request(message)

    if analysis.get("is_study_plan_request", False):
        # Generate and store study plan
        response = await s.generate_schedule(message)
        p.set_study_plan(response)
    else:
        # Generate general chat response
        response = await s.generate_chat_response(message)

    return JSONResponse(content=response)
