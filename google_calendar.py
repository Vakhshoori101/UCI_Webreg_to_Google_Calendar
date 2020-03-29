from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from config import config

class Calendar():

    def __init__(self):
        # Scope for reading and writing to Calendar
        scopes = ["https://www.googleapis.com/auth/calendar"]

        flow = InstalledAppFlow.from_client_secrets_file(config["client_secret_path"], scopes=scopes)
        self.credentials = flow.run_console()

        self.service = build("calendar", "v3", credentials=self.credentials)

        # ask user which calendar to edit
        result = self.service.calendarList().list().execute()
        for i,c in enumerate(result["items"]):
            print(f'Calendar {i + 1}: {c["id"]}')

        calendar_index = int(input("Choose number corresponding to wanted calendar to be edited: "))
        self.calendar_id = result["items"][calendar_index - 1]["id"]

    def prepare_time(self, time:str)->list:
        ''' Prepares the time checking if class starts in the morning of afternoon
            Puts it in Army time, ex: 14:30 '''
        start_time, end_time = time.split("-")
        start_hour, start_minute = start_time.split(":")
        end_hour, end_minute = end_time.split(":")

        # if the starting time is after 1pm
        if (1 <= int(start_hour) < 8) or (8 <= int(start_hour) <= 9 and end_time[-2:] == "pm"):
            start_hour = int(start_hour) + 12
            if end_minute[-2:] == "pm":
                end_minute = end_minute[:-2]
            end_hour = int(end_hour) + 12
        else:
            if 1 <= int(end_hour) < 8:
                end_hour = int(end_hour) + 12
            else:
                end_hour = int(end_hour)
            start_hour = int(start_hour)

        start_minute = int(start_minute)
        end_minute = int(end_minute)

        return [start_hour, start_minute, end_hour, end_minute]

    def prepare_day(self, days:list, first_day = 30, start_month = 3)->list:
        ''' Prepares the day, depending on what day of the week the first class starts'''
        d = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4}
        first_day += d[days[0]]
        if first_day > 31:
            first_day -= 31
            start_month += 1
        recurring_days = ""
        recurring_days = ",".join(days)
        return [first_day, recurring_days, start_month]

    def prepare_dates(self, time:str, days:list, start_year = 2020, end_year = 2020, end_month = 6, end_day = 6)->list:
        ''' Prepares start class and end class in datetime format with the last day in a string'''
        start_hour, start_minute, end_hour, end_minute = self.prepare_time(time)
        first_day, recurring_days, start_month = self.prepare_day(days)
        start_time = datetime(start_year, start_month, first_day, start_hour, start_minute, 0)
        end_time = datetime(start_year, start_month, first_day, end_hour, end_minute, 0)
        until = str(end_year) + "{:02d}".format(end_month) + "{:02d}".format(end_day)

        return [start_time, end_time, until, recurring_days]

    def create_event(self, course:dict):
        ''' Creates event in correct format to be sent'''
        summary = course["Name"]
        location = course["Location"]
        course_id = course["Number"]
        start_time, end_time, until, recurring_days = self.prepare_dates(course["Time"], course["Days"])

        event = {
            'summary': str(summary),
            'location': str(location),
            'description': "Course ID: " + str(course_id),
            'start': {
                'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'America/Los_Angeles',
            },
            'recurrence': [
                'RRULE:FREQ=WEEKLY;UNTIL=' + until + ';BYDAY=' + recurring_days

            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        return event

    def add_event(self, course):
        ''' Adds event to user's google calendar'''
        self.service.events().insert(calendarId=self.calendar_id, body=self.create_event(course)).execute()