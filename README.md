## RaspberryProjects
Read more about my projects at my blog: https://syllepsis.live/  

Contains code run on Raspberry Pi's, primarily at a hobby farm logging data.  
The primary log file is: fiveteenMinuteLog.py  
Which is a mishmash of actions which are broken down a bit in their own files in DevelopmentFiles


The environment file keyFiles.ini (hidden) hides the API keys from Github.   
It is formatted as recommended in the `configparser` documentation:  

```
[APIkeys]
SE_apiKey: XXXXXXXXXXXXXXX
SE_site: NNNNNN
AW_apiKey: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
AW_applicationKey: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXYZ

[Other]
Name: 'The Lord Ruler'
Opposite: Dalinar
```


## References:

### To Google Sheets and temperature probe operation
 Reference: https://www.raspberrypi.org/forums/viewtopic.php?t=104169  

### More references used with temperature probes
 https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/hardware  
 http://www.reuk.co.uk/wordpress/raspberry-pi/ds18b20-temperature-sensor-with-raspberry-pi/  
 connecting multiple temperature sensors  
 http://www.reuk.co.uk/wordpress/raspberry-pi/connect-multiple-temperature-sensors-with-raspberry-pi/  

### On logging Raspberry Pi system status
 From: https://www.raspberrypi.org/forums/viewtopic.php?t=22180  

### API References
 https://www.solaredge.com/sites/default/files/se_monitoring_api.pdf  
 https://www.ambientweather.com/community.html  
 https://github.com/ambient-weather/api-docs  
 https://help.waterdata.usgs.gov/faq/automated-retrievals    
 *using both Solar Edge and Ambient Weather require owning one of their systems*  
