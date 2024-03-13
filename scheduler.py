from datetime import datetime, timezone, timedelta
import os.path
import pytz
import random

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


#time_max = datetime(2024, 3, 23, 23, 59, 59).isoformat() + "Z"

    # # Call the Calendar API
#now =  datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time


class CalendarScheduler():
   
    def __init__(self):
        self.creds    = self.setup_creds()
        self.service  = build("calendar", "v3", credentials=self.creds)

    def setup_creds(self):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
                      
        return creds


    def create_event(self,start, end, summary = "Test", location = "Dallas", description = "Appointment for X-RAY", colorId = 6):
        event = {
            "summary"       : summary,
            "location"      : location,
            "description"   : description,
            "colorId"       : colorId,
            "start"         : start,
            "end"           : end
        }
        try: 
            event = self.service.events().insert(calendarId="primary", body = event).execute()
            return True
        except:
            return False



    def list_events(self,time_min, time_max):
        events_result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax = time_max, 
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        
        return events

    
    def convert_timezone(self, start, timezone='America/Chicago'):
        timestamp = datetime.fromisoformat(start)
        timestamp = timestamp.replace(tzinfo=None)

        # Define timezones
        source_timezone = pytz.timezone(timezone)  # GMT+5:30
        target_timezone = pytz.timezone('America/Chicago')  # Chicago timezone

        # Convert timezone
        timestamp_source_timezone = source_timezone.localize(timestamp)
        timestamp_chicago_timezone = timestamp_source_timezone.astimezone(target_timezone)

        return timestamp_chicago_timezone.isoformat()

        
        
    '''
        Provides user with availiable timeslots
    '''
    def availiable_timeslots(self, time_min, time_max):
        events = self.list_events(time_min, time_max)
        start_day = datetime.fromisoformat(time_min[:-1]).date()
        end_day   = datetime.fromisoformat(time_max[:-1]).date()
        
        print(start_day,  end_day)
        # Define start and end times
        time_slots   = []
        total_slots  = {}
        start_time = datetime.strptime('08:00', '%H:%M')
        end_time = datetime.strptime('17:00', '%H:%M')

        # Initialize current time
        current_time = start_time
        current_day  = start_day
        
        # Traverse from start time to end time
        while current_time <= end_time:
            time_slots.append(current_time.strftime('%H:%M'))
            current_time += timedelta(hours=1)
            
        while current_day <= end_day:
            total_slots[current_day] = time_slots
            current_day += timedelta(days=1)
        
        booked_slots={}
        for event in events:
            booked = self.convert_timezone(event['start']['dateTime'], timezone=event['start']['timeZone'])
            timestamp = datetime.fromisoformat(booked)
            # Extract date and hour
            date = timestamp.date()
            hour = timestamp.time().strftime('%H:%M')
            booked_slots.setdefault(date, []).append(hour)
        
        availiable_timeslots={}

        for key in total_slots.keys():
            if key in booked_slots:
                availiable_timeslots[key] = [x for x in total_slots[key] if x not in booked_slots[key]]
            else:
                availiable_timeslots[key] = time_slots #["Aavailable 9 to 5"]
            
            
        return availiable_timeslots
            
            
    def reschedule_event(self,id, start,end ,time_min, time_max):
        # # Call the Calendar API
        tot_events = self.list_events(time_min, time_max)
        try:
            for event in tot_events:
                title = event['summary']
                member_id = int(title.split(" ")[0])
                ## Assumption only one event
                #5568420
                if member_id == id:
                    print("Found the member id")
                    event_id = event['id']
                    description = event['description']
                    self.delete_events(event_id)
                    ## create and event
                    print("start time and end time", start, end)
                    self.create_event(start, end,summary=title, description = description)   
                            
                    return 1
                
            return 0
        except Exception as e:
            print("error")
            return 0
        

    
    def delete_user_test(self, id, time_min, time_max):
        tot_events = self.list_events(time_min, time_max)
        print(tot_events)
        try:
            for event in tot_events:
                title = event['summary']
                member_id = int(title.split(" ")[0])
                if member_id == id:
                    print("Found the member id")
                    event_id = event['id']
                    self.delete_events(event_id)
                    
            return 1
        except Exception as e:
            print("error")
            return 0
        
        

    def delete_all_events(self,time_min, time_max):
        events = self.list_events(time_min, time_max)
        for event in events:
            event_id = event['id']
            self.service.events().delete(calendarId="primary", eventId = event_id).execute()


    def delete_events(self,eventId):
        self.service.events().delete(calendarId='primary', eventId=eventId).execute()



    def create_date_time_object(self, year, month, day, hours, minutes, seconds):
        offset = timezone(timedelta(hours=-5))
        return datetime(year, month, day, hours, minutes, seconds, tzinfo = offset).isoformat()
        
    
    def generate_random_id(self):
        # Generate a random number of digits between 5 and 10
        # num_digits = random.randint(5,7)
        num_digits = 5

        # Generate a random ID with the specified number of digits
        random_id = ''.join(random.choices('0123456789', k=num_digits))

        return random_id

    def generate_random_name(self):
        first_names = ['Alice', 'Bob', 'Charlie', 'David', 'Eva', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack', 'Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor']
        random_first_name = random.choice(first_names)

        return f"{random_first_name}"


    def generate_random_test(self):
        test_names = ['X-RAY', 'Ultrasound', 'ECG']
        return random.choice(test_names)


    def mock_data_creation(self):
        for day in range(18,23):
            hours = random.sample(range(8, 17), 5)
            for hour in hours:
                name = self.generate_random_name()
                test = self.generate_random_test()
                summary = self.generate_random_id() + "  " + name + " " + test
                description = "Appointment for " + test
                colorId = random.randint(3,10)
                
                
                start_time = self.create_date_time_object(2024, 3, day, hour, 00, 00 )
                end_time   = self.create_date_time_object(2024, 3, day, hour+1, 00,00)
                start = {'dateTime' : start_time, 'timezone' : "America/Chicago"}
                end   = {'dateTime' : end_time, 'timezone'   : "America/Chicago"}
                
                self.create_event(start=start, end=end, summary=summary, description=description, colorId=colorId)
        

# if __name__ == "__main__":
#   main()

