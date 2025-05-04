import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List


class ScheduleItem(BaseModel):
    day: str
    start: str
    end: str
    title: str
    description: str


class PlanResponse(BaseModel):
    schedule: List[ScheduleItem]


today = datetime.datetime.now()


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


def convert_events_to_calendar(study_plan):
    event_list = []  # Etkinlikleri tutacağımız liste

    current_date = today  # Başlangıç tarihi
    for item in study_plan:
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
