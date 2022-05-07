# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 23:15:17 2021

@author: Sugocy
"""

class progress():            
    def bar(\
        progress, total, barLength = 20, \
        barStr = ['Progress','Busy','Done'], \
        barMarker = 'o', endMark = '\r'):
        
        # Calc
        percent = float(progress) * 100 / total
        bar   = '-' * int(percent/100 * barLength - 1) + barMarker
        spaces  = '-' * (barLength - len(bar))
        
        # Print
        if progress == total:   # if bar finished
            print("\r%s: [%s%s] %d%% %s" % \
                  (barStr[0], bar, spaces, percent, barStr[2]), end="\n")
        else:                   # If bar in progress
            print("\r%s: [%s%s] %d%% %s" % \
                  (barStr[0], bar, spaces, percent, barStr[1]), end=endMark)

            
# #-- Example --# #  
if __name__ == "__main__":       
    import time
    mx = 100; dt = 0.1 # 10 second loadbar      
    for kk in range(0,mx):
        progress.bar(kk, mx-1); time.sleep(dt);
        