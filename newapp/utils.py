from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from oauth2client import file, tools, client

from django.conf import settings
import os.path as path
import datetime
import requests


import os
from datetime import timedelta
import datetime
import pytz

import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

service_account_email = 'smart-calendar-service@true-winter-408610.iam.gserviceaccount.com'

CLIENT_SECRET_FILE = 'creds.p12'
current_dir = path.dirname(__file__)

SCOPES = 'https://www.googleapis.com/auth/calendar'
scopes = [SCOPES]

json_file_path = path.join(current_dir, 'client_secret.json')

def build_service():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(filename=json_file_path,scopes=SCOPES)

    http = credentials.authorize(httplib2.Http())

    service = build('calendar', 'v3', http=http)

    return service


def create_event():
    service = build_service()

    start_datetime = datetime.datetime.now(tz=pytz.utc)
    event = service.events().insert(calendarId='onitahcelestine@gmail.com', body={
        'summary': 'Foo',
        'description': 'Bar',
        'start': {'dateTime': start_datetime.isoformat()},
        'end': {'dateTime': (start_datetime + timedelta(minutes=15)).isoformat()},
    }).execute()

    print(event)

# # Define the scopes for accessing Google Calendar API
# SCOPES = ['https://www.googleapis.com/auth/calendar']

# # Get the directory of the current module (utils.py)
# current_dir = path.dirname(__file__)

# # Construct the path to clientsecret.json
# json_file_path = path.join(current_dir, 'credentials.json')

# def add_event_to_google_calendar(appointment, request):
#     doctor = None
#     nurse = None
#     email = None
#     if appointment.doctor:
#         doctor_email = appointment.doctor.user.user.email
#     else:
#         nurse_email = appointment.nurse.user.user.email
    
#     if doctor != None:
#         email = doctor_email
#     else:
#         emial = nurse_email
#     creds = None
#     # The file token.json stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if path.exists("token.json"):
#         creds = Credentials.from_authorized_user_file("token.json", SCOPES)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 json_file_path, SCOPES
#             )
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open("token.json", "w") as token:
#             token.write(creds.to_json())

#     try:
#         service = build("calendar", "v3", credentials=creds)

#         # Calculate the duration of the appointment in minutes
#         duration_minutes = (appointment.end_time - appointment.start_time).total_seconds() / 60

#         # Calculate the end time of the appointment based on the duration
#         end_time = appointment.start_time + datetime.timedelta(minutes=duration_minutes)

#         time_zone = settings.TIME_ZONE

#         # Create event payload
#         event = {
#             'summary': 'Surgery Appointment',
#             'description': 'Patient: {}'.format(request.user.first_name),
#             'start': {
#                 'dateTime': appointment.start_time.strftime('%Y-%m-%dT%H:%M:%S'),
#                 'timeZone': time_zone,
#             },
#             'end': {
#                 'dateTime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
#                 'timeZone': time_zone,
#             },
#             "attendees": [{
#                 'email': email}]
#         }
#         print(event)
#         # Call the API to insert the event
#         event = service.events().insert(calendarId='primary', sendNotifications=True, body=event).execute()
#         print('Event created: %s' % (event.get('htmlLink')))
#     except:
#         print("An error occured")

def get_coordinates_from_address(address):
    """
    Get latitude and longitude coordinates from an address using Google Maps Geocoding API.
    """
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": settings.GOOGLE_MAPS_API_KEY 
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            # Handle error response
            error_message = data["error_message"] if "error_message" in data else "Unknown error"
            raise Exception(f"Error: {data['status']} - {error_message}")
    except Exception as e:
        # Handle request errors
        raise Exception(f"Error: {str(e)}")
