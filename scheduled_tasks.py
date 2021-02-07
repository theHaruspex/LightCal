from datetime import datetime

import schedule
import time
from twilio.rest import Client

import calendar_manipulation as f
from Configuration import config

account_sid = config.ACCOUNT_SID
auth_token = config.AUTH_TOKEN
reminder_offset = config.reminder_offset
twilio_num = config.TWILIO_NUMBER
personal_num = config.PERSONAL_NUMBER


def send_today_events():
    body = f.today_events()
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=body,
        from_=twilio_num,
        to=personal_num)
    return


def send_tomorrow_events():
    body = f.tomorrow_events()
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=body,
        from_=twilio_num,
        to=personal_num)
    return


def event_reminder(event):
    body = f.display_event(event) + '\n' + 'Reminder'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=body,
        from_=twilio_num,
        to=personal_num)
    return


def populate_event_list():
    event_list = []
    today_events = f.get_events(f.today_range())
    for event in today_events:
        start_time_iso = event['start'].get('dateTime', event['start'].get('date'))
        start_time_dt = datetime.strptime(start_time_iso, '%Y-%m-%dT%H:%M:%S-08:00')
        reminder_time = str(start_time_dt + reminder_offset)[11:16]
        event_list.append((event, reminder_time))
    return event_list


# todo: check if this still works
def populate_task_list():
    task_list = []
    event_list = populate_event_list()
    for entry in event_list:
        event = entry[0]
        reminder_time = entry[1]
        task = schedule.every().day.at(reminder_time).do(event_reminder, event)
        task_list.append(task)
    return task_list


def depopulate_task_list(task_list):
    for task in task_list:
        task_list.remove(task)
    return task_list


def print_time():
    print(datetime.now())
    return


task_list = populate_task_list()
schedule.every().day.at(config.event_summary_time).do(send_today_events)
schedule.every().day.at(config.tom_event_summary_time).do(send_tomorrow_events)
schedule.every().day.at("00:01").do(populate_task_list)
schedule.every(1).minutes.do(print_time)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as error:
        print(f'{error}, restarting.')
        continue
