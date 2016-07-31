import sys
import os
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

for sg in sensor_data.sensorReadings:
    payload = {}
    payload["reading"] = int(sg.reading)
    payload["dateTimeString"] = sg.dateTimeString

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

