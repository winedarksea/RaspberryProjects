# This is scheduled to run every fiveteen minutes by Cron on the a server

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

# import sys
import time
import datetime
import os
import gspread
import configparser as configparser
import requests

# set to True to test
test_run = False

os.chdir("/home/colin/FarmLog")

#operating stats of linux server
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
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

# Define destinations
GDOCS_SPREADSHEET_NAME = 'FarmWeather'
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# access JSON credentials file provided by Google API
ac_name = 'FarmSensor-dc6049b112a2.json'
try:
    gc = gspread.service_account(filename=ac_name)
except Exception:
    from oauth2client.service_account import ServiceAccountCredentials
    credentials = ServiceAccountCredentials.from_json_keyfile_name(ac_name, scope)
    gc = gspread.authorize(credentials)

'''
# Test code
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
        worksheet = gc.open(spreadsheet).sheet1
        return worksheet
    except Exception:
        print('Unable to login and get spreadsheet.  Check credentials, spreadsheet name.')

# written this way for a code that was supposed to time.sleep() itself between logs
worksheet = None
if worksheet is None:
    worksheet = login_open_sheet(GDOCS_SPREADSHEET_NAME)

# Record data from system and sensors
try:
    memoryUsage = os.popen('''awk '/MemTotal/{t=$2}/MemAvailable/{a=$2}END{print 100-100*a/t"%"}' /proc/meminfo''').readline().replace("\n","")
except Exception:
    memoryUsage = 'Error'
try:
    CPU_temp = getCPUtemperature()
except Exception:
    CPU_temp = "Error"
try:
    CPU_Pct=str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))
except Exception:
    CPU_Pct = "Error"
try:
    DISK_stats = getDiskSpace()
    DISK_used = (DISK_stats[1])
except Exception:
    DISK_used = "Error"

tempA = "Deprecated"
tempB = "Deprecated"
tempC = "Deprecated"
###########################################################
# Part Two: Accessing internet loaded data

# from documentation for configparser, query function
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except Exception:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

# get keys from the environment file
Config = configparser.ConfigParser()
# Env file location on laptop versus raspberry
#Config.read(r"C:\Users\Owner\Documents\Personal\Projects\WeatherStation\keyFiles.ini")

#Config.read("/home/pi/RaspberryProjects/keyFiles.ini")
Config.read("keyFiles.ini")
# Get keys for Solar Edge
SE_apiKey = ConfigSectionMap('APIkeys')['se_apikey']
SE_site = ConfigSectionMap("APIkeys")['se_site']
# Get AmbientWeather api keys
AW_apiKey = ConfigSectionMap("APIkeys")['aw_apikey']
AW_applicationKey = ConfigSectionMap("APIkeys")['aw_applicationkey']


# Get current solar panel data from Solar Edge
#Current Day System Energy
startDate = str(datetime.datetime.now().year) + "-" + str(datetime.datetime.now().month) + "-" + str(datetime.datetime.now().day)
endDate = str(datetime.datetime.now().year) + "-" + str(datetime.datetime.now().month) + "-" + str(datetime.datetime.now().day)
SE_energy_url = "https://monitoringapi.solaredge.com/site/" + SE_site + "/energy.json?startDate=" + startDate + "&endDate=" + endDate + "&api_key=" + SE_apiKey
# Watt hours
try:
    solar_daily_watt_hours = requests.get(SE_energy_url).json()['energy']['values'][0]['value']
except Exception:
    solar_daily_watt_hours = "Error"
if solar_daily_watt_hours == None:
    solar_daily_watt_hours = 0

# Current Power Generation
SE_power_url = "https://monitoringapi.solaredge.com/site/" + SE_site + "/overview.json?" + "api_key=" + SE_apiKey
# in Watts
try:
    solar_current_watts = requests.get(SE_power_url).json()['overview']['currentPower']['power']
except Exception:
    solar_current_watts = "Error"
if solar_current_watts == None:
    solar_current_watts = 0

# Additional Solar Records:
startTime = startDate + "%20" + str(datetime.datetime.now().hour) + ":" + str((datetime.datetime.now()).minute) + ":" + str((datetime.datetime.now()- datetime.timedelta(seconds = 1)).second)
endTime = endDate + "%20" + str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute) + ":" + str(datetime.datetime.now().second)
SE_power_urlALT = "https://monitoringapi.solaredge.com/site/" + SE_site + "/power.json?startTime=" + startTime + "&endTime=" + endTime + "&api_key=" + SE_apiKey
try:
    solar_current_wattsALT = requests.get(SE_power_urlALT).json()['power']['values'][0]['value']
except Exception:
    solar_current_wattsALT = "Error"
if solar_current_wattsALT == None:
    solar_current_wattsALT = 0

# Get Weather Station Data
AW_url = "https://api.ambientweather.net/v1/devices?apiKey=" + AW_apiKey + "&&applicationKey=" + AW_applicationKey
#station = requests.get('https://api.ambientweather.net/v1/devices?apiKey=c122e4908df646b2bbc6d90dc4a445208f7c409a9f494d2a8825ba05dede0187&&applicationKey=c35cdb6f01074008a29d2f50bed978a0b93a2279d30e47178ed742f33c03a220')
try:
    station = requests.get(AW_url)
    station_dict = station.json()
except Exception:
    #fake JSON to collect errors, probably inefficient but it works
    station_dict = [{"macAddress":"Something","lastData":{"dateutc":"Error","winddir":"Error","windspeedmph":"Error","windgustmph":"Error","maxdailygust":"Error","tempf":"Error","hourlyrainin":"Error","eventrainin":"Error","dailyrainin":"Error","weeklyrainin":"Error","monthlyrainin":"Error","totalrainin":"Error","baromrelin":"Error","baromabsin":"Error","humidity":"Error","tempinf":"Error","humidityin":"Error","uv":"Error","solarradiation":"Error","feelsLike":"Error","dewPoint":"Error","lastRain":"Error","date":"Error"},"info":{"name":"FarmSensorNet","location":"Wabasha"}}]
station_winddir = station_dict[0]['lastData']['winddir'] #compass degrees
station_windspeedmph = station_dict[0]['lastData']['windspeedmph']
station_windgustmph = station_dict[0]['lastData']['windgustmph']
station_maxdailygust = station_dict[0]['lastData']['maxdailygust']
station_tempf = station_dict[0]['lastData']['tempf']
#if station_tempf is float:
#    station_tempf = round((station_tempf - 32) * (5/9),1) # to Celsius for consistency
station_hourlyrainin = station_dict[0]['lastData']['hourlyrainin']
station_eventrainin = station_dict[0]['lastData']['eventrainin']
station_dailyrainin = station_dict[0]['lastData']['dailyrainin']
station_weeklyrainin = station_dict[0]['lastData']['weeklyrainin']
station_monthlyrainin = station_dict[0]['lastData']['monthlyrainin']
station_totalrainin = station_dict[0]['lastData']['totalrainin']
station_baromrelin = station_dict[0]['lastData']['baromrelin']
station_baromabsin = station_dict[0]['lastData']['baromabsin']
station_humidity = station_dict[0]['lastData']['humidity']
station_tempinf = station_dict[0]['lastData']['tempinf'] #indoor temperature
#if station_tempinf is float:
try:
    station_tempinC = round((((station_tempinf) - 32.0) * (0.5555555556)),1) # to Celsius for consistency
    station_tempC =  round((((station_tempf) - 32.0) * (0.5555555556)),1) # to Celsius for consistency
except Exception:
    station_tempinC = "Error"
    station_tempC = 'Error'
station_humidityin = station_dict[0]['lastData']['humidityin'] #indoor humidity
station_uv = station_dict[0]['lastData']['uv']
station_solarradiation = station_dict[0]['lastData']['solarradiation']
station_feelsLike = station_dict[0]['lastData']['feelsLike']
station_dewPoint = station_dict[0]['lastData']['dewPoint']
station_lastRain = station_dict[0]['lastData']['lastRain']
station_date = station_dict[0]['lastData']['date']
station_dateutc = station_dict[0]['lastData']['dateutc']


# Get USGS Water Service Data
try:
    zumbro = requests.get('https://waterservices.usgs.gov/nwis/iv/?sites=05374900&format=json')
    zumbro_dict = zumbro.json()
    
    zumbro_water_temp = "Deprecated"
    zumbro_discharge = "Deprecated"
    zumbro_gage_height = "Deprecated"
    zumbro_turbidity = "Deprecated"
    for num_vars in range(len(zumbro_dict['value']['timeSeries'])):
        varName = zumbro_dict['value']['timeSeries'][num_vars]['variable']['variableName']
        if varName == 'Gage height, ft':
            zumbro_gage_height = float(zumbro_dict['value']['timeSeries'][num_vars]['values'][0]['value'][0]['value']) # height in feet
        if varName == 'Streamflow, ft&#179;/s':
            zumbro_discharge = float(zumbro_dict['value']['timeSeries'][num_vars]['values'][0]['value'][0]['value']) # cubic feet per second

except Exception:
    zumbro_water_temp = "Error"
    zumbro_discharge = "Error"
    zumbro_gage_height = "Error"
    zumbro_turbidity = "Error"

try:
    # reads stations decommissioned, now using Prescott, WI
    reads = requests.get('https://waterservices.usgs.gov/nwis/iv/?sites=05344500&format=json')
    reads = requests.get('https://waterservices.usgs.gov/nwis/iv/?sites=05355260&format=json')
    reads_dict = reads.json()
    
    reads_water_temp = "Deprecated"
    reads_discharge = "Deprecated"
    reads_gage_height = "Deprecated"
    reads_sensor_velocity = "Deprecated"
    for num_vars in range(len(reads_dict['value']['timeSeries'])):
        varName = reads_dict['value']['timeSeries'][num_vars]['variable']['variableName']
        if varName == 'Gage height, ft':
            reads_gage_height = float(reads_dict['value']['timeSeries'][num_vars]['values'][0]['value'][0]['value']) # height in feet
        if varName == 'Streamflow, ft&#179;/s':
            reads_discharge = float(reads_dict['value']['timeSeries'][num_vars]['values'][0]['value'][0]['value']) # cubic feet per second

except Exception:
    reads_water_temp = "Error"
    reads_discharge = "Error"
    reads_gage_height = "Error"
    reads_sensor_velocity = "Error"



############################################################
# Part Three: Upload
# Now upload all the data to the Google Sheet
# it's a bit slower than 'append row' but also more flexible to edit
if not test_run:
    try:
        next_row = next_available_row(worksheet)
        worksheet.append_row(["temp"])
        worksheet.update_acell("A{}".format(next_row), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        worksheet.update_acell("B{}".format(next_row), "prod3")
        worksheet.update_acell("C{}".format(next_row), memoryUsage)
        worksheet.update_acell("D{}".format(next_row), CPU_Pct)
        worksheet.update_acell("E{}".format(next_row), DISK_used)
        worksheet.update_acell("F{}".format(next_row), tempA)
        worksheet.update_acell("G{}".format(next_row), tempB)
        worksheet.update_acell("H{}".format(next_row), tempC)
        worksheet.update_acell("I{}".format(next_row), solar_daily_watt_hours)
        worksheet.update_acell("J{}".format(next_row), solar_current_watts)
        worksheet.update_acell("K{}".format(next_row), solar_current_wattsALT)
        worksheet.update_acell("L{}".format(next_row), reads_water_temp)
        worksheet.update_acell("M{}".format(next_row), reads_discharge)
        worksheet.update_acell("N{}".format(next_row), reads_gage_height)
        worksheet.update_acell("O{}".format(next_row), reads_sensor_velocity)
        worksheet.update_acell("P{}".format(next_row), zumbro_water_temp)
        worksheet.update_acell("Q{}".format(next_row), zumbro_discharge)
        worksheet.update_acell("R{}".format(next_row), zumbro_gage_height)
        worksheet.update_acell("S{}".format(next_row), zumbro_turbidity)
        worksheet.update_acell("T{}".format(next_row), station_winddir)
        worksheet.update_acell("U{}".format(next_row), station_windspeedmph)
        worksheet.update_acell("V{}".format(next_row), station_windgustmph)
        worksheet.update_acell("W{}".format(next_row), station_maxdailygust)
        worksheet.update_acell("X{}".format(next_row), station_tempC)
        worksheet.update_acell("Y{}".format(next_row), station_hourlyrainin)
        worksheet.update_acell("Z{}".format(next_row), station_eventrainin)
        worksheet.update_acell("AA{}".format(next_row), station_dailyrainin)
        worksheet.update_acell("AB{}".format(next_row), station_weeklyrainin)
        worksheet.update_acell("AC{}".format(next_row), station_monthlyrainin)
        worksheet.update_acell("AD{}".format(next_row), station_totalrainin)
        worksheet.update_acell("AE{}".format(next_row), station_baromrelin)
        worksheet.update_acell("AF{}".format(next_row), station_baromabsin)
        worksheet.update_acell("AG{}".format(next_row), station_humidity)
        worksheet.update_acell("AH{}".format(next_row), station_tempinC)
        worksheet.update_acell("AI{}".format(next_row), station_humidityin)
        worksheet.update_acell("AJ{}".format(next_row), station_uv)
        worksheet.update_acell("AK{}".format(next_row), station_solarradiation)
        worksheet.update_acell("AL{}".format(next_row), station_feelsLike)
        worksheet.update_acell("AM{}".format(next_row), station_dewPoint)
        worksheet.update_acell("AN{}".format(next_row), station_lastRain)
        worksheet.update_acell("AO{}".format(next_row), station_date)
        worksheet.update_acell("AP{}".format(next_row), station_dateutc)
        
        #worksheet.append_row((datetime.datetime.now(),"test", read_tempA(), read_tempB(), read_tempC()))
    except Exception:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed at the top of the loop.
        print('Append error')
        worksheet = None


if not test_run:
    output_file = "FiveteenMinuteData.csv"
else:
    output_file = 'weather_test.csv'

# Record to local storage as well
try:
    with open(output_file, "a") as myfile:
        myfile.write("\n{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"prod3", memoryUsage, CPU_Pct,
                DISK_used, tempA, tempB, tempC,solar_daily_watt_hours,solar_current_watts,
                reads_water_temp,reads_discharge,zumbro_gage_height,reads_sensor_velocity,
                zumbro_water_temp, zumbro_discharge,zumbro_gage_height,zumbro_turbidity,
                station_winddir,station_windspeedmph,station_windgustmph,station_maxdailygust,station_tempC,
                station_hourlyrainin,station_eventrainin,station_dailyrainin,station_weeklyrainin,
                station_monthlyrainin,station_totalrainin,station_baromrelin,station_baromabsin,
                station_humidity, station_tempinC,station_humidityin,station_uv,station_solarradiation,
                station_feelsLike,station_dewPoint,station_lastRain,station_date,station_dateutc))
except Exception:
    with open(output_file, "a") as myfile:
        myfile.write("\n{}, {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"log error"))

# Just to be clear:
# sys.exit(0)
