
from scheduler import CalendarScheduler
from datetime  import datetime, timedelta
from whisper_inference_pipeline.generate import Whisper
import re
from model import GLiNER

model = GLiNER.from_pretrained("urchade/gliner_base")
#model = None

sch          = CalendarScheduler()
whisper      = Whisper()


start_day = datetime.utcnow().day

now      = datetime(2024, 3, start_day, 00, 00, 00).isoformat() + "Z"


time_max = datetime(2024, 3, start_day + 7, 23, 59, 59).isoformat() + "Z"


def process_audio(audio):
    return whisper.extract(audio, path=True)

def get_ehr_details(text):
    ehr_labels = ["test", "date", "time", "patient_id", "person"]
    sentences = text.split(".")
    ehr_data= {}
    for sentence in sentences[:-1]:
        entities = model.predict_entities(sentence, ehr_labels)
        for entity in entities:
            if (entity['label'] == 'date' or entity['label'] == 'time') and 'test' not in ehr_data:
                continue
            if entity['label'] not in ehr_data:
                ehr_data[entity['label']] = entity
            
    return ehr_data


def get_reschedule_details(text):
    sch_labels = ["test", "date"]
    entities = model.predict_entities(text, sch_labels)
    sch_data = {}
    for entity in entities:
        if entity['label'] not in sch_data:
            sch_data[entity['label']] = entity
            
    return sch_data
    



def schedule_earliest_appointement(ehr_data, time_min = now, time_max = time_max):
    slots = sch.availiable_timeslots(time_min=time_min, time_max=time_max)
    for key, value in slots.items():
        start_time = sch.create_date_time_object(key.year,key.month,key.day,00,00,00)
        
        if(len(value) == 0):
            continue
            # return "No Appointments availiable on {}".format(get_calendar_format(start_time))
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
        
    return "No Appointments availiable for next week"


def reschedule_earliest_appointement(ehr_data, date, time_min = now, time_max = time_max):
    month, day   = process_date(date)
    if(not month and not day ):
        return "Please include which month and day you want to reschedule your appointment."
    now      = datetime(2024, 3, 18, 00, 00, 00).isoformat() + "Z"
    sch.delete_user_test(int(ehr_data['patient_id']['text']), time_min=now, time_max=time_max)
    now      = datetime(2024, month, day, 8, 00, 00).isoformat() + "Z"
    time_max = datetime(2024, month, 24, 23, 59, 59).isoformat() + "Z"
    return schedule_earliest_appointement(ehr_data, time_min=now, time_max=time_max)


def get_calendar_format(dateTimeString):
    # Convert datetime string to a datetime object
    dateTime = datetime.fromisoformat(dateTimeString)

    # Extract day, hour, minute, and second components
    day = dateTime.strftime('%A')  # Get day name (e.g., Monday)
    month_name  = dateTime.strftime("%B")
    time = dateTime.strftime('%I:%M %p')
    
    # # Adjust time for timezone
    # timezone_offset = dateTime.utcoffset()
    # if timezone_offset:
    #     timezone_adjusted_time = dateTime + timezone_offset
    #     time = timezone_adjusted_time.strftime('%H %p')
        
    print(dateTimeString, day, time)
        
    return str(dateTime.day) + " " + month_name + "," + day + " " + str(time)


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
    else:
        return None, None
        
    return month, 20 
        
            
def process_time(time):
    matches = re.search(r'(\d{1,2}:\d{2}\s*[apAP]\.?[mM])', time)
    if matches:
        return datetime.strptime(matches.group(1), '%I:%M %p')
    return None


def reschedule_appointment(date, id, time = None):
    pass
    
    
    # month, day   = process_date(date)
    # time         = process_time(time)
    # slots        = sch.availiable_timeslots(time_min=now, time_max=time_max)
    # start_time   = sch.create_date_time_object(2024, month, day, time.hour, 00, 00)
    # end_time     = sch.create_date_time_object(2024, month, day, time.hour+1, 00, 00)
    # events       = sch.list_events(start_time, end_time)
    # if events:
    #     start_day = datetime(2024, month, day,8,00,00).isoformat() + 'Z'
    #     end_day   = datetime(2024, month, day,17,00,00).isoformat() + 'Z'
    #     slots   = sch.availiable_timeslots(time_min = start_day, time_max = end_day)
    #     for key, values in slots.items():
    #         return "We dont have the slot availiable at {} on {}. These are the availiable slots {' '.join(slots)}".format(key.strftime('%B'), key.day)
    # else:
    #     # Then create the appointment for the schedule time
    #     start = {'dateTime' : start_time, 'timezone' : "America/Chicago"}
    #     end   = {'dateTime' : end_time, 'timezone'   : "America/Chicago"}
    #     status = sch.reschedule_event(id, start, end, time_min=now, time_max=time_max)
    #     if(status):
    #         return "Appointment Scheduled at {} on {}".format(time, date)
        
        


        
        

