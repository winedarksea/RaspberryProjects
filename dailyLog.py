### To Google Sheets
# Reference: https://www.raspberrypi.org/forums/viewtopic.php?t=104169


import sys
import time
import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import requests
# r = request.get(‘https://github.com/timeline.json’)
#print r.text, or print r.json

#operating stats
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

#for Google log
def next_available_row(worksheet):
    str_list = filter(None, worksheet.col_values(1))  # fastest
    return str(len(str_list)+1)

# Google Docs account email, password, and spreadsheet name.
GDOCS_SPREADSHEET_NAME = 'DailyFarmLog'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 60 * 60 * 24


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('FarmSensor-dc6049b112a2.json', scope)


def login_open_sheet(spreadsheet):
	"""Connecting to Google Docs to write first measurement to spreadsheet."""
	try:
		#gc = gspread.login(email, password)
                gc = gspread.authorize(credentials)
		worksheet = gc.open(spreadsheet).sheet1
		return worksheet
	except:
		print 'Unable to login and get spreadsheet.  Check credentials, spreadsheet name.'
		sys.exit(1)


print 'Writing measurements to {0}'.format(GDOCS_SPREADSHEET_NAME)
print 'Press Ctrl-C to stop.'
worksheet = None

	# Login if necessary.
if worksheet is None:
    worksheet = login_open_sheet(GDOCS_SPREADSHEET_NAME)


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
    next_row = next_available_row(worksheet)
    worksheet.update_acell("A{}".format(next_row), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    worksheet.update_acell("B{}".format(next_row), "test4")
    worksheet.update_acell("C{}".format(next_row), CPU_temp)
    worksheet.update_acell("D{}".format(next_row), CPU_Pct)
    worksheet.update_acell("E{}".format(next_row), DISK_used)
    worksheet.update_acell("F{}".format(next_row), tempA)

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
    with open("TwelveMinuteData.csv", "a") as myfile:
        myfile.write("\n{}, {}, {}, {}, {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"test", CPU_temp, CPU_Pct, DISK_used, tempA, tempB, tempC))
except:
    with open("TwelveMinuteData.csv", "a") as myfile:
        myfile.write("\n{}, {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"log error"))
sys.exit(0)
