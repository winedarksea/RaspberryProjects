# From: https://www.raspberrypi.org/forums/viewtopic.php?t=22180
import os

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
CPU_temp = getCPUtemperature()
CPU_Pct=str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))
#CPU_usage = getCPUuse()
DISK_stats = getDiskSpace()
DISK_used = (DISK_stats[1])
print(CPU_Pct)