import sys
import os
from datetime import datetime, timedelta
import json
import Carelink
import requests

def hilite(string, status, bold):
    attr = []
    if status >= 200 and status < 400:
        # green
        attr.append('32')
    elif status >= 400 and status < 500:
        # red
        attr.append('31')
    if bold:
        attr.append('1')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

def _create_DATEOBJ(data, tmz_delta, format):
    date = datetime.strptime(data, format)
    if tmz_delta:
        date += tmz_delta
    return date

def dateToStr(date):
    # Since datetime doesn't understand parsing timezones
    return date.strftime("%Y-%m-%dT%H:%M:%S") + "-04:00"

def create_DATE(data, tmz_delta):
    date = _create_DATEOBJ(data, tmz_delta, "%m/%d/%y")
    return dateToStr(date)

def create_TIME(data, tmz_delta):
    date = _create_DATEOBJ(data, tmz_delta, "%H:%M:%S")
    time_struct = date.timetuple()
    hour = time_struct[3] * 60 * 60
    min =  time_struct[4] * 60
    sec =  time_struct[5]
    return hour + min + sec

def create_TIMESTAMP(data, tmz_delta):
    date = _create_DATEOBJ(data, tmz_delta, "%b %d, %Y %H:%M:%S")
    return dateToStr(date)

session = Carelink.startSession()

CARELINK_USER = os.environ['carelink_user']
CARELINK_PW = os.environ['carelink_pw']

if not Carelink.login(session, CARELINK_USER, CARELINK_PW):
    sys.stderr.write("Unable to log in")
    exit(1)

sensor_data = Carelink.sensor_24_hours(session)
if sensor_data == None:
    sys.stderr.write("No sensor data")
    exit(1)


API_KEY_HEADER = "X-Cairo-API-Key"
APP_ID_HEADER = "X-Cairo-Application-ID"

API_KEY = os.environ['cairo_api_key']
APP_ID = os.environ['cairo_app_id']

URL = "https://cairo.glucloser.com:4443/pump/sensor/data/upload"
HEADERS = {API_KEY_HEADER: API_KEY, APP_ID_HEADER: APP_ID, "Content-Type": "application/json"}

isTTY = sys.stdout.isatty()

# Don't have any way to get the GMT offset of the device
# TODO(nl) EST/EDT
tz_delta = timedelta(hours=4)

for sg in sensor_data.sensorReadings:
    payload = {}
    payload["reading"] = int(sg.reading)
    payload["dateTimeString"] = dateToStr(create_TIMESTAMP(sg.dateTimeString, tz_delta))

    if not payload:
        print "Empty payload, skipping"
        continue

    print "Uploading ", payload

    response = requests.put(URL, data=json.dumps(payload), headers=HEADERS)

    if isTTY and response.status_code >= 400 and response.status_code < 500:
        print hilite("Response code " + str(response.status_code) + " => " + response.text, response.status_code, True)
        exit()
    else:
        print hilite("Response code " + str(response.status_code) + " => " + response.text, response.status_code, False)

