import subprocess as sp
import mpmath as mpm
import time

# Set decimal precision for mpm
mpm.mp.dps = 22 # This means mpm numbers are 22*3.33 bit, precise
                # enough for comparison of 17 digit floats

AS_T2_FILE = "T2_PARSED.out"
TA_LOC_FILE = "TA_LOCAL.txt"
CNC_FILE = "TAL_AS_COINCIDENCE.txt"

# Main loop
p1 = sp.Popen(['tail','-f',TA_LOC_FILE],stdout=sp.PIPE)
# All this business is O(n^2), which sucks, but I see no
#way around this. To be thorough we must compare each individual time stamp
#to be absolutely certain we don't miss a coincidence
seconds_old = p1.stdout.readline().split('.')[0]
tal_list = ""
t3_timer = time.time()
while True:
  tal_str = p1.stdout.readline() # Blocking call to tail buffer
  tal_list += tal_str
  seconds_new = tal_str.split('.')[0]
  if seconds_new != seconds_old and len(tal_list) > 50 :
    # We have a list of events in one second, look for coincidences
    time.sleep(1) # Auger south data is delayed by 1s
    p2 = sp.Popen(['tail','-n','70',AS_T2_FILE],stdout=sp.PIPE)
    as_t2_lst = p2.stdout.read(-1).split('\n')[:-1]
    tal_list = tal_list.split('\n')
    for local in tal_list[:-2]:
      try:
        x1 = mpm.mpf(local)
      except:
        break
      for south in as_t2_lst:
        x2 = mpm.mpf(south)
        diff = abs(float(x1-x2))
        # T3 issued for coincidence, and no T3 in progress
        if diff < 30e-6 and time.time() - t3_timer > 500.:
          with open(CNC_FILE,'a') as F:
            F.write("%s %s %.6f\n" %(local,south,diff))
          south_sec = south.split('.')[0]
          south_micro = south.split('.')[1]
          # T3 away!
          t3_timer = time.time()
          sp.Popen(['./cl','T','%s' %south_sec,'%s' %south_micro,'30'])
          break
      else:
        continue
      break
    tal_list = ''
  seconds_old = seconds_new
