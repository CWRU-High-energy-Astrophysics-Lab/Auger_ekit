import math
import time
import datetime as dt
import subprocess as sp
import sys

def utcFromString(x):
  split_x = x.split(',')
  int_x = map(int,split_x)
  right_order = [2,1,0,3,4,5]
  int_x = [int_x[i] for i in right_order]
  return int_x

secsInWeek = 604800 
secsInDay = 86400 
gpsEpoch = (1980, 1, 6, 0, 0, 0)  # (year, month, day, hh, mm, ss)

def gpsFromUTC(year, month, day, hour, minute, sec, leapSecs=17): 
  """converts UTC to GPS second

  Original function can be found at: http://software.ligo.org/docs/glue/frames.html

  GPS time is basically measured in (atomic) seconds since  
  January 6, 1980, 00:00:00.0  (the GPS Epoch) 

  The GPS week starts on Saturday midnight (Sunday morning), and runs 
  for 604800 seconds.  

  Currently, GPS time is 17 seconds ahead of UTC
  While GPS SVs transmit this difference and the date when another leap 
  second takes effect, the use of leap seconds cannot be predicted.  This 
  routine is precise until the next leap second is introduced and has to be 
  updated after that.

  SOW = Seconds of Week 
  SOD = Seconds of Day 

  Note:  Python represents time in integer seconds, fractions are lost!!! 
  """ 
  secFract = sec % 1 
  epochTuple = gpsEpoch + (-1, -1, 0) 
  t0 = time.mktime(epochTuple) 
  t = time.mktime((year, month, day, hour, minute, sec, -1, -1, 0))  
  # Note: time.mktime strictly works in localtime and to yield UTC, it should be 
  #       corrected with time.timezone 
  #       However, since we use the difference, this correction is unnecessary. 
  # Warning:  trouble if daylight savings flag is set to -1 or 1 !!! 
  t = t + leapSecs
  tdiff = t - t0
  gpsSOW = (tdiff % secsInWeek)  + secFract
  gpsWeek = int(math.floor(tdiff/secsInWeek))
  gpsDay = int(math.floor(gpsSOW/secsInDay))
  gpsSOD = (gpsSOW % secsInDay)
  gps_tuple = (gpsWeek, gpsSOW, gpsDay, gpsSOD)
  return int(gps_tuple[0] * secsInWeek + gps_tuple[1])

now = dt.datetime.now() # Datetime tuple

datestr = "%s%02d%02d" %(now.year,now.month,now.day)
p = sp.Popen(['ssh','root@192.168.3.101','ls','-l','/data/Events/%s' %datestr],stdout=sp.PIPE)
time.sleep(20)
dirlist = p.stdout.readlines()
if len(dirlist) == 0:
	sys.exit()
dirlist.pop(0)
dirlist_gps = [0]*len(dirlist)

i = 0
for k in dirlist:
	x = k.replace('\n','')
	x = x.split(' ')
	x = x[-1]
	x = x.split('.')
	x = x[0]
	yr,mo,d = int(x[:4]),int(x[4:6]),int(x[6:8])
	h,m,s = int(x[9:11]),int(x[11:13]),int(x[13:15])
	dirlist_gps[i] = gpsFromUTC(yr,mo,d,h,m,s)
	i += 1

i = 0
clist_file = 'TAL_AS_COINCIDENCE.txt'
f = open(clist_file,'r')
elist = f.readlines()
f.close()

if len(elist) == 0:
	sys.exit()

n1 = len(elist)
n2 = len(dirlist_gps)

time.sleep(660)

for i in range(n1):
	as_ts = elist[i]
	as_ts = int(as_ts[:10])
	for j in range(n2):
		gps_diff = as_ts - dirlist_gps[j]
		if gps_diff > 0:
			# Found north file associated with event
			filename = dirlist[j-1].split(' ')[-1].replace('\n','')[:-4] + "*"
			sp.Popen(['ssh','root@192.168.3.101','rsync','-ah','/data/Events/%s/%s' %(datestr,filename),
				'augertaupload@129.22.134.40::north/Events/%s/' %datestr])

# Grab muon data
sp.Popen(['ssh','root@192.168.3.101','rsync','-ah','/data/Muons/%s/*' %datestr,
		'augertaupload@129.22.134.40::north/Muons/%s/' %datestr])

# Grab monitoring data
sp.Popen(['ssh','root@192.168.3.101','rsync','-ah','/data/Monitor/%s/*' %datestr,
		'augertaupload@129.22.134.40::north/Monitor/%s/' %datestr])

