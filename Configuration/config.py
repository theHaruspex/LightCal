from __future__ import print_function
from datetime import timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

'''Global Constants'''
MONTH_DICT = {
    1: 'jan',
    2: 'feb',
    3: 'mar',
    4: 'apr',
    5: 'may',
    6: 'jun',
    7: 'jul',
    8: 'aug',
    9: 'sep',
    10: 'oct',
    11: 'nov',
    12: 'dec'
}
TIMEZONE_DICT = dict(LINT=timedelta(seconds=50400), CHADT=timedelta(seconds=49500), NZDT=timedelta(seconds=46800),
                     ANAT=timedelta(seconds=43200), AEDT=timedelta(seconds=39600), ACDT=timedelta(seconds=37800),
                     AEST=timedelta(seconds=36000), ACST=timedelta(seconds=34200), JST=timedelta(seconds=32400),
                     ACWST=timedelta(seconds=31500), CST=timedelta(days=-1, seconds=64800),
                     WIB=timedelta(seconds=25200), MMT=timedelta(seconds=23400), BST=timedelta(seconds=21600),
                     NPT=timedelta(seconds=20700), IST=timedelta(seconds=19800), UZT=timedelta(seconds=18000),
                     AFT=timedelta(seconds=16200), GST=timedelta(days=-1, seconds=79200), IRST=timedelta(seconds=12600),
                     MSK=timedelta(seconds=10800), EET=timedelta(seconds=7200), CET=timedelta(seconds=3600),
                     GMT=timedelta(0), CVT=timedelta(days=-1, seconds=82800), ART=timedelta(days=-1, seconds=75600),
                     NST=timedelta(days=-1, seconds=73800), VET=timedelta(days=-1, seconds=72000),
                     EST=timedelta(days=-1, seconds=68400), MST=timedelta(days=-1, seconds=61200),
                     PST=timedelta(days=-1, seconds=57600), AKST=timedelta(days=-1, seconds=54000),
                     MART=timedelta(days=-1, seconds=52200), HST=timedelta(days=-1, seconds=50400),
                     NUT=timedelta(days=-1, seconds=46800), AoE=timedelta(days=-1, seconds=43200))

'''Twilio Credentials'''
ACCOUNT_SID = 'redacted'
AUTH_TOKEN = 'redacted'
TWILIO_NUMBER = 'redacted'
PERSONAL_NUMBER = 'redacted'

'''Google Calendar Options'''
timezone = 'PST'
PRIMARY_CALENDAR = 'primary'  # Google's Cal API takes 'primary' as an argument
SCOPES = ['https://www.googleapis.com/auth/calendar']
TIMEZONE_OFFSET = TIMEZONE_DICT[timezone]

'''Scheduled Tasks Configuration'''
reminder_offset = timedelta(minutes=-30)  # in minutes before event start
event_summary_time = '08:30'  # when to send the day's event summary, *in military format*
tom_event_summary_time = '18:00'

'''Google Authentification Flow'''
creds = None
config_directory = os.path.dirname(os.path.abspath(__file__)) + '/'
pickle_path = config_directory + 'token.pickle'
json_path = config_directory + 'credentials.json'

if os.path.exists(config_directory + 'token.pickle'):
    with open(pickle_path, 'rb') as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            json_path, SCOPES)
        creds = flow.run_local_server(port=0)
    with open(pickle_path, 'wb') as token:
        pickle.dump(creds, token)
SERVICE = build('calendar', 'v3', credentials=creds)