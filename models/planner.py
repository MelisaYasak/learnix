import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List


today = datetime.datetime.now()
study_plan_result = None


def set_study_plan(result):
    """Set the study plan result that can be accessed globally"""
    global study_plan_result
    study_plan_result = result
    return study_plan_result


def get_study_plan():
    """Get the current study plan result"""
    global study_plan_result
    return study_plan_result


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
    elif day_name.lower() == 'tomorrow':
        target_weekday = today.weekday()+1
    else:
        target_weekday = weekday_map[day_name]  # Hedef haftanın gününü al

    # Eğer hedef gün bugün ya da sonraki bir günse
    days_diff = (target_weekday - today_weekday) % 7
    next_target_date = start_date + datetime.timedelta(days=days_diff)

    return next_target_date


def convert_events_to_calendar(study_plan):
    event_list = []  # List to store events
    schedule_list = study_plan['schedule']
    print(schedule_list)
    current_date = today.date()  # Starting date

    for item in schedule_list:
        # Access dictionary items consistently using dictionary syntax
        target_day = item['day']  # Planned day (e.g., 'Monday')
        event_start_time = item['start']  # Start time
        event_end_time = item['end']  # End time

        # Find the target day's date
        target_date = get_next_weekday_date(target_day, current_date)

        # Create event start and end times
        # Fix the time format to '%H:%M' (hours:minutes)
        start_time = datetime.datetime.combine(
            target_date,
            datetime.datetime.strptime(event_start_time, '%H:%M').time()
        ).replace(tzinfo=datetime.timezone.utc)

        end_time = datetime.datetime.combine(
            target_date,
            datetime.datetime.strptime(event_end_time, '%H:%M').time()
        ).replace(tzinfo=datetime.timezone.utc)

        # Create the event
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

        # Add the event to the list
        event_list.append(event)

    return event_list
