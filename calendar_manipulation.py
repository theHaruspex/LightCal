from __future__ import print_function
from datetime import datetime, date, timedelta
from googleapiclient.errors import HttpError
from Configuration import config


calendar_id = config.PRIMARY_CALENDAR
month_list = config.MONTH_DICT
timezone_offset = config.TIMEZONE_OFFSET
service = config.SERVICE


def title_except(string):
    articles = ['a', 'an', 'of', 'the', 'is', 'at']
    word_list = string.split(' ')  # re.split behaves as expected
    final = [word_list[0].capitalize()]
    for word in word_list[1:]:
        final.append(word if word in articles else word.capitalize())
    return " ".join(final)


def today_range():
    midnight_today = datetime.combine(date.today(), datetime.min.time())
    midnight_today_utc = midnight_today - timezone_offset
    midnight_tomorrow_utc = midnight_today_utc + timedelta(days=1)
    str_midnight_today = str(midnight_today_utc).replace(' ', 'T') + 'Z'
    str_midnight_tomorrow = str(midnight_tomorrow_utc).replace(' ', 'T') + 'Z'
    return str_midnight_today, str_midnight_tomorrow


def tomorrow_range():
    pst_to_utc_tomorrow = -timezone_offset + timedelta(days=1)
    midnight_today = datetime.combine(date.today(), datetime.min.time())
    midnight_tomorrow_utc = midnight_today + pst_to_utc_tomorrow
    midnight_next_day_utc = midnight_tomorrow_utc + timedelta(days=1)
    str_midnight_today = str(midnight_tomorrow_utc).replace(' ', 'T') + 'Z'
    str_midnight_tomorrow = str(midnight_next_day_utc).replace(' ', 'T') + 'Z'
    return str_midnight_today, str_midnight_tomorrow


def get_events(time_range):
    min_range = time_range[0]
    max_range = time_range[1]
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=min_range,
        timeMax=max_range,
        singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events


def search_events(search_term, time_range):
    lower_search_term = search_term.lower()
    events = get_events(time_range)
    search_results = []
    for event in events:
        lower_event_summary = event['summary'].lower()
        if lower_search_term in lower_event_summary:
            search_results.append(event)
    return search_results


def convert_gTime_to_time(dt):
    event_time = (dt.split('T')[1])[:5]
    dt_in_24h = datetime.strptime(event_time, "%H:%M")
    target_hour_str = str(dt_in_24h)[11:13]
    target_minute_str = str(dt_in_24h)[14:16]
    target_hour = int(target_hour_str)
    if target_hour > 12:
        target_hour -= 12
        suffix = 'PM'
    else:
        suffix = 'AM'
    formatted_time = f'{target_hour}:{target_minute_str} {suffix}'
    return formatted_time


def convert_datetime_to_date(dt):
    event_date = (dt.split('T')[0])
    year, month, day = event_date.split('-')
    month_str = title_except(month_list[int(month)])
    formatted_date = f'{month_str} {day}, {year}'
    return formatted_date


def today_events():
    event_list = search_events('', today_range())
    if not event_list:
        return 'No events today :)'
    else:
        str_event_list = []
        for event in event_list:
            raw_start = event['start'].get('dateTime', event['start'].get('date'))
            raw_end = event['end'].get('dateTime', event['end'].get('date'))
            start = convert_gTime_to_time(raw_start)
            end = convert_gTime_to_time(raw_end)
            str_event_list.append((f"{start} - {end}:", f"{event['summary']}"))

        event_str = "Today's Events:\n"
        for event in str_event_list:
            event_str += event[0] + "\n"
            event_str += event[1] + "\n\n"
    return event_str


def tomorrow_events():
    event_list = search_events('', tomorrow_range())
    if not event_list:
        return 'No events tomorrow :)'
    else:
        str_event_list = []
        for event in event_list:
            raw_start = event['start'].get('dateTime', event['start'].get('date'))
            raw_end = event['end'].get('dateTime', event['end'].get('date'))
            start = convert_gTime_to_time(raw_start)
            end = convert_gTime_to_time(raw_end)
            str_event_list.append((f"{start} - {end}:", f"{event['summary']}"))

        event_str = "Tomorrow's Events:\n"
        for event in str_event_list:
            event_str += event[0] + "\n"
            event_str += event[1] + "\n\n"
    return event_str


def sms_to_iso(sms):
    lower_sms = sms.lower()
    split = lower_sms.split(' ')
    #month = month_list.index(split[0])
    month = list(month_list.keys())[list(month_list.values()).index(split[0])]
    day = int(split[1])
    if len(split) == 3:
        year = int(split[2])
    else:
        year = datetime.now().year
    iso_date = date(year, month, day)
    return iso_date



def iso_date_to_utc_daterange(iso_date):
    target_datetime = datetime.combine(iso_date, datetime.min.time())
    target_datetime_utc = target_datetime - timezone_offset
    target_datetime_utc_2 = target_datetime_utc + timedelta(days=1)
    target_range = str(target_datetime_utc), str(target_datetime_utc_2)
    str_target_range = []
    for item in target_range:
        target = item.replace(' ', 'T') + 'Z'
        str_target_range.append(target)
    return str_target_range


def sms_to_daterange(sms):
    iso_date = sms_to_iso(sms)
    daterange = iso_date_to_utc_daterange(iso_date)
    return daterange


def log_activity(activity_type, event):
    current_datetime = str(datetime.now())
    event_id = event['id']
    event_title = event['summary']
    log_entry = f'{current_datetime} ‖ {activity_type} ‖ {event_id} ‖ {event_title}' + '\n'
    with open('/Users/rossvaughn/PycharmProjects/calandar_to_sms/activity_log/add_del_log.txt', 'a') as file:
        file.write(log_entry)
    return


def delete_event(event):
    try:
        service.events().delete(
            calendarId=calendar_id,
            eventId=event['id']).execute()
        log_activity('Delete', event)
        return event
    except HttpError:
        return "Event not found."


def delete_from_user_input(event_input):
    split_sms = event_input.split(' ')
    if 'on' in split_sms:
        split_sms.remove('on')
    query = ' '.join(split_sms[:-2]).lower()
    raw_date = ' '.join(split_sms[-2:])
    date_range = sms_to_daterange(raw_date)
    try:
        event = search_events(query, date_range)[0]
        deleted_event = delete_event(event)
        return deleted_event
    except IndexError:
        return



def create_event(event_input):
    title_input = title_except(event_input)
    event = service.events().quickAdd(
        calendarId=calendar_id,
        text=title_input).execute()
    log_activity('Create', event)
    return event


def display_event(event):
    if event == 'Event not found.':
        return event
    event_name = event['summary']
    raw_event_start = event['start'].get('dateTime', event['start'].get('date'))
    start_date = convert_datetime_to_date(raw_event_start)
    start_time = convert_gTime_to_time(raw_event_start)
    raw_event_end = event['end'].get('dateTime', event['start'].get('date'))
    end_time = convert_gTime_to_time(raw_event_end)
    return f'{event_name} ‖ {start_date} ‖ {start_time} - {end_time}'


def get_most_recent_added_event():
    with open('/Users/rossvaughn/PycharmProjects/calandar_to_sms/activity_log/add_del_log.txt', 'r') as file:
        all_entries = file.readlines()
    for entry in all_entries:
        if 'Create' in entry:
            target_entry = entry
    key = 'datetime', 'activity_type', 'event_id', 'event_name'
    value = target_entry.split(' ‖ ')
    event_id = value[2]
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    activity_entry = dict(zip(key, value))
    return event
