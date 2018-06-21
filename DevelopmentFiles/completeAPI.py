import configparser
import requests
import datetime

# from documentation for configparser, query function
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

# get keys from the environment file
# it would be much easier to just type SE_apiKey = 'XXXXXX' but this harder way keeps off github
Config = configparser.ConfigParser()
Config.read(r"C:\Users\Owner\Documents\Personal\Projects\WeatherStation\keyFiles.ini")
# Get keys for Solar Edge
SE_apiKey = ConfigSectionMap("APIkeys")['se_apikey']
SE_site = ConfigSectionMap("APIkeys")['se_site']
# Get AmbientWeather api keys
AW_apiKey = ConfigSectionMap("APIkeys")['aw_apikey']
AW_applicationKey = ConfigSectionMap('APIkeys')['aw_applicationkey']


# Get current solar panel data from Solar Edge
#Current Day System Energy
startDate = str(datetime.datetime.now().year) + "-" + str(datetime.datetime.now().month) + "-" + str(datetime.datetime.now().day)
endDate = str(datetime.datetime.now().year) + "-" + str(datetime.datetime.now().month) + "-" + str(datetime.datetime.now().day)
SE_energy_url = "https://monitoringapi.solaredge.com/site/" + SE_site + "/energy.json?startDate=" + startDate + "&endDate=" + endDate + "&api_key=" + SE_apiKey
# Watt hours
try:
    solar_daily_watt_hours = requests.get(SE_energy_url).json()['energy']['values'][0]['value']
except:
    solar_daily_watt_hours = "Connection Error"
if solar_daily_watt_hours == None:
    solar_daily_watt_hours = 0

# Current Power Generation
startTime = startDate + "%20" + str(datetime.datetime.now().hour) + ":" + str((datetime.datetime.now()).minute) + ":" + str((datetime.datetime.now()- datetime.timedelta(seconds = 1)).second)
endTime = endDate + "%20" + str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute) + ":" + str(datetime.datetime.now().second)
SE_power_url = "https://monitoringapi.solaredge.com/site/" + SE_site + "/power.json?startTime=" + startTime + "&endTime=" + endTime + "&api_key=" + SE_apiKey
# Watts
try:
    solar_current_watts = requests.get(SE_power_url).json()['power']['values'][0]['value']
except:
    solar_current_watts = "Connection Error"
if solar_current_watts == None:
    solar_current_watts = 0
#print(solar_current_watts)

# Get Weather Station Data
AW_url = "https://api.ambientweather.net/v1/devices?apiKey=" + AW_apiKey + "&&applicationKey=" + AW_applicationKey
#station = requests.get('https://api.ambientweather.net/v1/devices?apiKey=c122e4908df646b2bbc6d90dc4a445208f7c409a9f494d2a8825ba05dede0187&&applicationKey=c35cdb6f01074008a29d2f50bed978a0b93a2279d30e47178ed742f33c03a220')
try:
    station = requests.get(AW_url)
    station_dict = station.json()
except:
    #fake JSON to collect errors, probably inefficient but it works
    station_dict = [{"macAddress":"Something","lastData":{"dateutc":"Error","winddir":"Error","windspeedmph":"Error","windgustmph":"Error","maxdailygust":"Error","tempf":"Error","hourlyrainin":"Error","eventrainin":"Error","dailyrainin":"Error","weeklyrainin":"Error","monthlyrainin":"Error","totalrainin":"Error","baromrelin":"Error","baromabsin":"Error","humidity":"Error","tempinf":"Error","humidityin":"Error","uv":"Error","solarradiation":"Error","feelsLike":"Error","dewPoint":"Error","lastRain":"Error","date":"Error"},"info":{"name":"FarmSensorNet","location":"Wabasha"}}]
station_winddir = station_dict[0]['lastData']['winddir'] #compass degrees
station_windspeedmph = station_dict[0]['lastData']['windspeedmph']
station_windgustmph = station_dict[0]['lastData']['windgustmph']
station_maxdailygust = station_dict[0]['lastData']['maxdailygust']
station_tempf = station_dict[0]['lastData']['tempf']
if station_tempf is float:
    station_tempf = round((station_tempf - 32) * (5/9),1) # to Celsius for consistency
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
if station_tempinf is float:
    station_tempinf = round((station_tempinf - 32) * (5/9),1) # to Celsius for consistency
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
    zumbro_water_temp = float(zumbro_dict['value']['timeSeries'][0]['values'][0]['value'][0]['value']) # degrees C
    zumbro_discharge = float(zumbro_dict['value']['timeSeries'][1]['values'][0]['value'][0]['value']) # cubic feet per second
    zumbro_gage_height = float(zumbro_dict['value']['timeSeries'][2]['values'][0]['value'][0]['value']) # height in feet
    zumbro_turbidity = float(zumbro_dict['value']['timeSeries'][3]['values'][0]['value'][0]['value']) # formazin nephelometric units (FNU)
except:
    zumbro_water_temp = "Error"
    zumbro_discharge = "Error"
    zumbro_gage_height = "Error"
    zumbro_turbidity = "Error"
try:
    reads = requests.get('https://waterservices.usgs.gov/nwis/iv/?sites=05355341&format=json')
    reads_dict = reads.json()
    #reads_dict['value']['timeSeries'][0]['values'][0]['value'][0]['value']
    reads_water_temp = float(reads_dict['value']['timeSeries'][0]['values'][0]['value'][0]['value']) # degrees F
    reads_water_temp = round((reads_water_temp - 32) * (5/9),1) # to Celsius for consistency
    reads_discharge = float(reads_dict['value']['timeSeries'][1]['values'][0]['value'][0]['value']) # cubic feet per second
    reads_gage_height = float(reads_dict['value']['timeSeries'][2]['values'][0]['value'][0]['value']) # height in feet
    reads_sensor_velocity = float(reads_dict['value']['timeSeries'][3]['values'][0]['value'][0]['value']) # feet per second

except:
    reads_water_temp = "Error"
    reads_discharge = "Error"
    reads_gage_height = "Error"
    reads_sensor_velocity = "Error"
