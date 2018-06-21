# This is scheduled to run every fiveteen minutes by Cron on the Raspberry

### To Google Sheets and temperature probe operation
# Reference: https://www.raspberrypi.org/forums/viewtopic.php?t=104169

### More references used with temperature probes
# https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/hardware
# http://www.reuk.co.uk/wordpress/raspberry-pi/ds18b20-temperature-sensor-with-raspberry-pi/
# connecting multiple temperature sensors
# http://www.reuk.co.uk/wordpress/raspberry-pi/connect-multiple-temperature-sensors-with-raspberry-pi/

### On logging Raspberry Pi system status
# From: https://www.raspberrypi.org/forums/viewtopic.php?t=22180

### API References
# https://www.solaredge.com/sites/default/files/se_monitoring_api.pdf
# https://www.ambientweather.com/community.html
# https://github.com/ambient-weather/api-docs
# https://help.waterdata.usgs.gov/faq/automated-retrievals

import sys
import time
import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import configparser
import requests

# opening sensor drivers for temperature probes
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
# Create functions to access temperature probe readings
def read_temp_rawA():
    device_file = '/sys/bus/w1/devices/28-04173060c6ff/w1_slave'
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp_rawB():
    device_file = '/sys/bus/w1/devices/28-04173041b9ff/w1_slave'
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp_rawC():
    device_file = '/sys/bus/w1/devices/28-0317302490ff/w1_slave'
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

#Celsius/Centigrade is selected, change return temp_c to return temp_f for Fahrenheit	
def read_tempA():
    lines = read_temp_rawA()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_rawA()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c

def read_tempB():
    lines = read_temp_rawB()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_rawB()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c
def read_tempC():
    lines = read_temp_rawC()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_rawC()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c

'''
to_print = read_tempC()
print "Temp is: % .2f  C" % to_print
sys.exit(1)
'''

#operating stats of Raspberry Pi
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

def getCPUuse():
    return(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip(\
)))

def getDiskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()
        if i==2:
            return(line.split()[1:5])

#helper function for Google log, to reach last row
def next_available_row(worksheet):
    str_list = filter(None, worksheet.col_values(1))  # fastest
    return str(len(str_list)+1)

# Define destinations
GDOCS_SPREADSHEET_NAME = 'FarmWeather'
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# access JSON credentials file provided by Google API
credentials = ServiceAccountCredentials.from_json_keyfile_name('FarmSensor-dc6049b112a2.json', scope)

'''
gc = gspread.authorize(credentials)
wks = gc.open("FarmWeather").sheet1
next_row = next_available_row(wks)
#wks.append_row("MAGIC")
wks.update_acell("A{}".format(next_row), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
wks.update_acell("B{}".format(next_row), read_tempA())
sys.exit(1)
'''

#Connecting to Google Docs to write first measurement to spreadsheet
def login_open_sheet(spreadsheet):
	try:
        gc = gspread.authorize(credentials)
		worksheet = gc.open(spreadsheet).sheet1
		return worksheet
	except:
		print 'Unable to login and get spreadsheet.  Check credentials, spreadsheet name.'
		sys.exit(1)

worksheet = None
	# Login if necessary.
if worksheet is None:
    worksheet = login_open_sheet(GDOCS_SPREADSHEET_NAME)
	#print(read_tempA())
 
	# Append the data in the spreadsheet, including the time
try:
    CPU_temp = getCPUtemperature()
except:
    CPU_temp = "Error"
try:
    CPU_Pct=str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))
except:
    CPU_Pct = "Error"
try:
    DISK_stats = getDiskSpace()
    DISK_used = (DISK_stats[1])
except:
    DISK_used = "Error"
try:
    tempA = read_tempA()
except:
    tempA = "SensorDown"
try:
    tempB = read_tempB()
except:
    tempB = "SensorDown"
try:
    tempC = read_tempC()
except:
    tempC = "SensorDown"


# Now upload all the data to the Google Sheet
try:
    next_row = next_available_row(worksheet)
    worksheet.update_acell("A{}".format(next_row), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    worksheet.update_acell("B{}".format(next_row), "test4")
    worksheet.update_acell("C{}".format(next_row), CPU_temp)
    worksheet.update_acell("D{}".format(next_row), CPU_Pct)
    worksheet.update_acell("E{}".format(next_row), DISK_used)
    worksheet.update_acell("F{}".format(next_row), tempA)
    worksheet.update_acell("G{}".format(next_row), tempB)
    worksheet.update_acell("H{}".format(next_row), tempC)
    #worksheet.append_row((datetime.datetime.now(),"test", read_tempA(), read_tempB(), read_tempC()))
except:
    # Error appending data, most likely because credentials are stale.
    # Null out the worksheet so a login is performed at the top of the loop.
    print 'Append error'
    worksheet = None
    #time.sleep(FREQUENCY_SECONDS)

	# Wait 30 seconds before continuing
	#print 'Measurement added to {0}'.format(GDOCS_SPREADSHEET_NAME)
	#time.sleep(FREQUENCY_SECONDS)

try:
    with open("FiveteenMinuteData.csv", "a") as myfile:
        myfile.write("\n{}, {}, {}, {}, {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"test", CPU_temp, CPU_Pct, DISK_used, tempA, tempB, tempC))
except:
    with open("FiveteenMinuteData.csv", "a") as myfile:
        myfile.write("\n{}, {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"log error"))
sys.exit(0)
