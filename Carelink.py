# Install the Python Requests library:
# `pip install requests`

import time
import sys
import requests
from lxml import html
from urlparse import urlparse
from datetime import datetime, timedelta

def startSession():
    return requests.session()


user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/601.3.9 (KHTML, like Gecko)     Version/9.0.2 Safari/601.3.9"

def download(session, url):
    try:
        response = session.get(
            url=url,
            headers={
            },
        )
        return response.content
        # print('Response HTTP Status Code: {status_code}'.format(
            # status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
            # content=response.content))
    except requests.exceptions.RequestException:
        # print('HTTP Request failed')
        return None


def request_all_reports(session):
    # All Reports
    # POST https://carelink.minimed.com/patient/main/requestProReport.do

    # TODO(nl): time zone
    startDate = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
    delta = timedelta(-7)
    startDate = startDate + delta
    startDateString = startDate.strftime("%Y-%m-%dT%H:%M:%S-04:00")

    endDate = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
    endDateString =  endDate.strftime("%Y-%m-%dT%H:%M:%S-04:00")

    clientTime = datetime.now()
    clientTimeString = clientTime.strftime("%m/%d/%y %I:M:%S %p")

    daysSelected = "" 
    d = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
    for i in range(1, 7):
        delta = timedelta(-1*i)
        daysSelected += (d + delta).strftime("%Y-%m-%dT%H:%M:%S-04:00")

    data = {
                "masterDuration": "2",
                "startDateString": startDateString,
                "endDateString": endDateString,
                "clientTimeString": clientTimeString,
                "selected[0]": "on",
                "selected[3]": "on",
                "customerID": "553090",
                "dailyDetails": "1,2,3",
                "selected[1]": "on",
                "selected[4]": "on",
                "dailySelected": endDateString,
                "selected[2]": "on",
                "selected[5]": "on",
            }
            
    try:
        response = session.post(
            url="https://carelink.minimed.com/patient/main/requestProReport.do",
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            },
            data=data,
        )
        page = html.fromstring(response.content)
        reportURL = page.xpath('//*[@id="content"]/form/@action')
        if len(reportURL) == 0:
            return None
        
        reportURL = reportURL[0]

        pageURL = urlparse(response.url)
        return "{}://{}{}".format(pageURL.scheme, pageURL.netloc, reportURL)
        # print('Response HTTP Status Code: {status_code}'.format(
            # status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
            # content=response.content))
    except requests.exceptions.RequestException:
        # print('HTTP Request failed')
        return None




def csv_export(session, start_date, end_date):
    """
    Fetches a csv export report for the date range. Date params should be strings
    of the format mm/dd/yyy.
    """
    # CSV Export
    # POST https://carelink.minimed.com/patient/main/selectCSV.do

    try:
        response = session.post(
            url="https://carelink.minimed.com/patient/main/selectCSV.do",
            params={
                "t": "11",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                "User-Agent": user_agent,
            },
            data={
                "datePicker2": start_date,
                "listSeparator": ",",
                "datePicker1": end_date,
                "report": "11",
                "customerID": "553090",
            },
        )
        #sys.stderr.write('Response HTTP Response Body: {content}\n'.format(
         #   content=response.content))
        return response.content
    except requests.exceptions.RequestException:
        sys.stderr.write('HTTP Request failed\n')
        sys.stderr.write('Response HTTP Status Code: {status_code}\n'.format(
            status_code=response.status_code))


def sensor_24_hours(session):
    # Sensor Last 24 Hours
    # GET https://carelink.minimed.com/patient/connect/ConnectViewerServlet

    #sys.stderr.write("Fetching 24 hour sensor data\n")

    try:
        response = session.get(
            url="https://carelink.minimed.com/patient/connect/ConnectViewerServlet",
            params={
                "cpSerialNumber": "NONE",
                "msgType": "last24hours",
                "requestTime": time.time(),
            },
            headers={
                "User-Agent": user_agent,
            },
        )
        #sys.stderr.write('Response HTTP Status Code: {status_code}\n'.format(
          #  status_code=response.status_code))
        # sys.stderr.write('Response HTTP Response Body: {content}'.format(
            # content=response.content))
        return sensor_data_from_json(response.json())
    except ValueError:
        #sys.stderr.write("JSON decoding failed\n")
        return None
    except requests.exceptions.RequestException:
        #sys.stderr.write('HTTP Request failed\n')
        return None

def login(session, username, password):
    # Login
    # POST https://carelink.minimed.com/patient/j_security_check

    #sys.stderr.write("Logging In\n")
    try:
        response = session.post(
            url="https://carelink.minimed.com/patient/j_security_check",
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                "User-Agent": user_agent
            },
            data={
                "j_password": password,
                "j_username": username,
                "j_character_encoding": "UTF-8",
            },
        )
        #sys.stderr.write('Response HTTP Status Code: {status_code}\n'.format(
        #    status_code=response.status_code))
        # sys.stderr.write('Response HTTP Response Body: {content}'.format(
            # content=response.content))
        return True
    except requests.exceptions.RequestException:
        #sys.stderr.write('HTTP Request failed\n')
        return False

def sensor_data_from_json(json):
    sd = SensorData()
    sd.lastSensorTimestampString = json["lastSensorTSAsString"]
    sd.sensorStateString = json["sensorState"]

    lastSG = json["lastSG"]
    if "sg" in lastSG and "datetime" in lastSG:
        sd.lastSensorReading = SensorReading(lastSG["sg"], lastSG["datetime"])

    insulin = json["activeInsulin"]
    if "amount" in insulin and "datetime" in insulin:
        sd.activeInsulin = Insulin(insulin["amount"], insulin["datetime"])

    for sg in json["sgs"]:
        if "sg" in sg and "datetime" in sg:
            sd.sensorReadings.append(SensorReading(sg["sg"], sg["datetime"]))
    
    return sd


class SensorReading(object):
    reading = 0.0
    dateTimeString = ""

    def __init__(self, r = 0.0, dt = ""):
        self.reading = r
        self.dateTimeString = dt

class Insulin(object):
    amount = 0.0
    dateTimeString = ""

    def __init__(self, a = 0.0, dt = ""):
        self.amount = a
        self.dateTimeString = dt

class SensorData(object):
    lastSensorTimestampString = ""
    sensorStateString = ""
    lastSensorReading = SensorReading()
    activeInsulin = Insulin()
    sensorReadings = []

    def __init__(self):
        pass
