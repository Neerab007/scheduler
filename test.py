

from scheduler import CalendarScheduler
from datetime  import datetime, timedelta

text = """
John Doe, patient id 110234, a 55-year-old male, has a medical history that includes hypertension and type 2 diabetes. To manage his conditions, he was prescribed a medication regimen.

For hypertension, John was initially prescribed Lisinopril at a daily dosage of 20 mg, administered orally. He started taking Lisinopril on May 5, 2021. Unfortunately, he developed an allergic reaction, experiencing rash and itching, which led to the discontinuation of Lisinopril on May 20, 2021.

To address his type 2 diabetes, John took Metformin, with a dosage of 1000 mg orally twice daily. He began taking Metformin on May 1, 2021. However, he encountered gastrointestinal upset, including nausea and diarrhea, resulting in an adjustment of his Metformin dosage on May 15, 2021.

As part of cardiovascular protection, John's healthcare provider advised him to take Aspirin, at a daily dosage of 81 mg orally, starting on June 1, 2021.

In summary, John's medical history, medication regimen, and the reasons for medication adjustments have been noted to ensure his ongoing care.

He has been advised to use X of Y with Z mg daily suffering for K.

After assessing the patient's symptoms of persistent cough and shortness of breath, I recommend scheduling a chest X-ray next week to evaluate the progression of the pulmonary condition and to assess for any underlying abnormalities or changes in lung function.

"""





sch = CalendarScheduler()

now      = datetime(2024, 3, 18, 8, 00, 00).isoformat() + "Z"
time_max = datetime(2024, 3, 24, 23, 59, 59).isoformat() + "Z"

print(datetime(2024, 3, 18, 9, 00, 00)+timedelta(hours=1))

sch.mock_data_creation()


#sch.delete_all_events(time_min=now, time_max=time_max)

#sch.mock_data_creation()
# pick the first available slot
# slots = sch.availiable_timeslots(time_min=now, time_max=time_max)


# id = int(ehr_data['patient_id']['text'])

# start_time   = sch.create_date_time_object(2024, 3, 18, 13, 00, 00)
# end_time     = sch.create_date_time_object(2024, 3, 18, 14, 00, 00)

# start = {'dateTime' : start_time, 'timezone' : "America/Chicago"}
# end   = {'dateTime' : end_time, 'timezone'   : "America/Chicago"}


# sch.reschedule_event(id, start, end, time_min=now, time_max=time_max)



# for key, value in slots.items():
#     print(key, value)
#     hr  = int(value[0].split(":")[0])
#     min = int(value[0].split(":")[1])

#     start_time = sch.create_date_time_object(key.year,key.month,key.day,hr,min,00)
#     end_time   = sch.create_date_time_object(key.year,key.month,key.day,hr+1,min,00)
#     summary = ehr_data['patient_id']['text'] + "  " + ehr_data['person']['text'] + " " + ehr_data['test']['text']
#     description =  "Appointment for " + ehr_data['test']['text']
#     start = {'dateTime' : start_time, 'timezone' : "America/Chicago"}
#     end   = {'dateTime' : end_time, 'timezone'   : "America/Chicago"}
#     sch.create_event(start, end, summary=summary, description=description)
   
        
#     dt = key+timedelta(hours=hr)+timedelta(minutes=min)
#     print(dt.isoformat() + "z")
    
#     break
    


### id = 110234


def schedule_earliest_appointement(ehr_data, time_min, time_max):
    slots = sch.availiable_timeslots(time_min=time_min, time_max=time_max)
    for key, value in slots.items():
        print(key, value)
        hr  = int(value[0].split(":")[0])
        min = int(value[0].split(":")[1])

        start_time = sch.create_date_time_object(key.year,key.month,key.day,hr,min,00)
        end_time   = sch.create_date_time_object(key.year,key.month,key.day,hr+1,min,00)
        summary = ehr_data['patient_id']['text'] + "  " + ehr_data['person']['text'] + " " + ehr_data['test']['text']
        description =  "Appointment for " + ehr_data['test']['text']
        start = {'dateTime' : start_time, 'timezone' : "America/Chicago"}
        end   = {'dateTime' : end_time, 'timezone'   : "America/Chicago"}
      
        if(sch.create_event(start, end, summary=summary, description=description)):
            return "Appointment Scheduled sucessfully on {}".format(get_calendar_format(start_time))
        
        else:
            return "System Down come back later"
        
        


    
    
    
    

def get_calendar_format(dateTimeString):
    # Convert datetime string to a datetime object
    dateTime = datetime.fromisoformat(dateTimeString)

    # Extract day, hour, minute, and second components
    day = dateTime.strftime('%A')  # Get day name (e.g., Monday)
    time = dateTime.strftime('%I:%M %p')  # Get time in HH:MM:SS format

    # Adjust time for timezone
    # timezone_offset = dateTime.utcoffset()
    # if timezone_offset:
    #     timezone_adjusted_time = dateTime + timezone_offset
    #     time = timezone_adjusted_time.strftime('%H %p')
        
    return str(dateTime.day) + " " + day + " " + str(time)



# from datetime import datetime, timedelta

# dateTimeString = '2024-03-18T13:00:00-05:00'

# print(get_calendar_format(dateTimeString))
#schedule_earliest_appointement(None, time_min=now, time_max=time_max)

def check_if_day(v):
    day = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    for i,d in enumerate(day):
        if d in v:
            return i
    
    return -1

def check_if_month(v):
    month = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sept', 'oct', 'nov', 'dec']
    for i,m in enumerate(month):
        if m in v:
            return i+1
        
    return 0   


import re

def extract_number_and_string(text):
    # Regular expression pattern
    pattern = r'(\d+)\s+(\D+)|(\D+)\s+(\d+)'

    # Find matches
    matches = re.match(pattern, text)

    # Extract number and string from matches
    if matches:
        number = matches.group(1) or matches.group(4)
        string = matches.group(2) or matches.group(3)
        return number, string
    else:
        return None, None



def process_date(date):
    month = check_if_month(date.lower())
    if month:
        day, string = extract_number_and_string(date)
        if day:
            return month, int(day)
        
    return month, 20 
        
            
def process_time(time):
    matches = re.search(r'(\d{1,2}:\d{2}\s*[apAP]\.?[mM])', time)
    if matches:
        return datetime.strptime(matches.group(1), '%I:%M %p')
    return None


def reschedule_appointment(time, date, id = 110234):
    month, day   = process_date(date)
    time         = process_time(time)
    slots        = sch.availiable_timeslots(time_min=now, time_max=time_max)
    start_time   = sch.create_date_time_object(2024, month, day, time.hour, 00, 00)
    end_time     = sch.create_date_time_object(2024, month, day, time.hour+1, 00, 00)
    events       = sch.list_events(start_time, end_time)
    if events:
        start_day = datetime(2024, month, day,8,00,00).isoformat() + 'Z'
        end_day   = datetime(2024, month, day,17,00,00).isoformat() + 'Z'
        slots   = sch.availiable_timeslots(time_min = start_day, time_max = end_day)
        for key, values in slots.items():
            return "We dont have the slot availiable at {} on {}. These are the availiable slots {' '.join(slots)}".format(key.strftime('%B'), key.day)
    else:
        # Then create the appointment for the schedule time
        start = {'dateTime' : start_time, 'timezone' : "America/Chicago"}
        end   = {'dateTime' : end_time, 'timezone'   : "America/Chicago"}
        status = sch.reschedule_event(id, start, end, time_min=now, time_max=time_max)
        if(status):
            return "Appointment Scheduled at {} on {}".format(time, date)
        


        

#reschedule_appointment('2:00 PM', 'march 18')
    

# text = "can you reschedule my X-RAY appointment to 2 PM on march 18 "    
    
# from ner_model import get_ehr_details, get_reschedule_details
# #res_data = get_ehr_details(text)

# res_data = get_reschedule_details(text)


# print(res_data)