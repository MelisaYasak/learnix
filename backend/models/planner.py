import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

today = datetime.datetime.now()
study_plan_result = None


def set_study_plan(result):
    """Store the generated study plan globally"""
    global study_plan_result
    study_plan_result = result
    return study_plan_result


def get_study_plan():
    """Retrieve the currently stored study plan"""
    global study_plan_result
    return study_plan_result


def get_next_weekday_date(day_name, start_date):
    """Return the next date matching the given weekday name starting from start_date"""
    weekday_map = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }

    today_weekday = start_date.weekday()

    if day_name.lower() == 'today':
        target_weekday = today.weekday()
    elif day_name.lower() == 'tomorrow':
        target_weekday = (today.weekday() + 1) % 7
    else:
        target_weekday = weekday_map.get(day_name, today_weekday)

    days_diff = (target_weekday - today_weekday) % 7
    return start_date + datetime.timedelta(days=days_diff)


def convert_events_to_calendar(study_plan):
    """Convert study plan dictionary to a list of calendar events"""
    event_list = []
    schedule_list = study_plan['schedule']
    current_date = today.date()

    for item in schedule_list:
        target_day = item['day']
        event_start_time = item['start']
        event_end_time = item['end']

        target_date = get_next_weekday_date(target_day, current_date)

        start_time = datetime.datetime.combine(
            target_date,
            datetime.datetime.strptime(event_start_time, '%H:%M').time()
        ).replace(tzinfo=datetime.timezone.utc)

        end_time = datetime.datetime.combine(
            target_date,
            datetime.datetime.strptime(event_end_time, '%H:%M').time()
        ).replace(tzinfo=datetime.timezone.utc)

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

        event_list.append(event)

    return event_list
