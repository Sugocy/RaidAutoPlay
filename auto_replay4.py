# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 18:38:46 2020

@author: Sugocy
"""

import numpy as np
from PIL import ImageGrab
from pynput.mouse import Button, Controller # conda install -c conda-forge pynput 
import matplotlib.pyplot as plt
import time
import sys
import win32gui as win
import cv2
from progressBar import progress


# Fillhole using fillFlood (cv)
def fillhole(iminp):
    # PREP
    imfill = iminp.copy()                     # Copy image
    h, w = iminp.shape[:2]                    # Width and height
    mask = np.zeros((h + 2, w + 2), np.uint8) # Seed-mask
    imfill = imfill.astype("uint8") 
    # FILL
    cv2.floodFill(imfill, mask, (0, 0), 255)
    # POST
    imfill_inv = cv2.bitwise_not(imfill)      # convert FlFill outp
    img_out = iminp | imfill_inv              # output
    return img_out



def gimmeClickLocation(im):
# Given color image - will return point to click

    dispon = False; #DEVstuff

    # BGR2GRAY
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)    
    # Backup
    imbu = im;
    # Image-ratio
    imrat = im.shape[1]/im.shape[0]
    
    # Ratio check
    rat = 16/9
    if imrat < rat*0.75 or imrat > rat*1.25:
        print('Change Raid-window ratio to 16 by 9 and restart.')
        sys.exit()
    
    # IMG PROCESSING # ---------------- #

    # Crop of image
    # These values are used to correct for cropping later on!
    xcrdt = 0.45; ycrdt = xcrdt * imrat # Crop ratio in image
    xcrop = [0]*2; ycrop = [0]*2;
    
    xcrop[0] = int(im.shape[1]*xcrdt); xcrop[1] = im.shape[1]
    ycrop[0] = int(im.shape[0]*ycrdt); ycrop[1] = im.shape[0]
    im = im[ycrop[0]:ycrop[1], xcrop[0]:xcrop[1]]
        
    # Threshold
    val , im = cv2.threshold(im, 128, 255, cv2.CHAIN_APPROX_NONE)    
    
    # Invert: rects white
    im = ~im 
   
    # FILL HOLES
    im = fillhole(im)
    
    # ERODE: smooth bg by eating fg 
    kernel = np.ones((3, 3), np.uint8)
    im = cv2.erode(im,kernel, iterations = 2)
    
    # INVERT: rects black
    im = ~im
    
    # FIND RECTANGLES
    contours , hierarchy = \
        cv2.findContours(im, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    
    # ANALYSE RECTANGLES 
    area = [0]*len(contours); rect  = [[0]*4]*len(contours); 
    check = [0]*len(contours); xnew = 10e6;
    for ii in range(len(contours)):
        
        # Countours to rectangle
        rect[ii] = list(cv2.boundingRect(contours[ii]))
        x = rect[ii][0]; y = rect[ii][1]; w = rect[ii][2]; h = rect[ii][3]
        # Area
        area[ii] =  (w*h)
        
        # If area smaller than 50% of full image: button
        if area[ii] < (im.shape[0]*im.shape[1])*0.5:    
            # Expect a button
            check[ii] = 1
           
            # ----------- SELECTING BUTTON HERE ------------- #
            # Most LEFT button (e.g. smallest X-axis value :D ) 
            if x < xnew: 
                sqoi = ii; xnew = x; ROI = [x,y,w,h]
                            
            if dispon:
                # Add rectangle to image for disp
                im = cv2.rectangle(im,(x,y),(x+w,h+y),(255,255,0), 2)    
    
    if not "ROI" in locals(): return 0, 0
    
    # Convert back to original image   
    ROI[0] = ROI[0] + xcrop[0];
    ROI[1] = ROI[1] + ycrop[0];
    
    # CLICK LOCATION
    click_loc = [0] * 2
    # REMEMBER: X/Y in CLICKLOC-WINDOWS ARE REVERSED :)
    click_loc[1] = round(ROI[0] + (ROI[2]/4));
    click_loc[0] = round(ROI[1] + (ROI[3]/4));
    
    
    if dispon:
        # Rect dection cropped image
        plt.Figure(); plt.imshow(im, cmap='jet'); plt.show()

        # Add to image
        imbu = cv2.rectangle(imbu,(ROI[0], ROI[1]),\
                          (ROI[0]+ROI[2],ROI[1]+ROI[3]),\
                          (255,255,0), 5)                
        # Rect detection in full image
        plt.Figure(); plt.imshow(im, cmap = 'jet'); plt.show()    
    
    return click_loc, ROI

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '',\
                      decimals = 1, length = 50, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = \
    ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()    
        
# Take screenshot of piano part on desktop
def gimmeImage(box):
    # Box – The crop rectangle, as a (left, upper, right, lower)-tuple
    img = ImageGrab.grab(bbox=box)
    img = np.asarray(img); # Convert image to array
    return img


def gimmeAppID():
    hwd = win.FindWindow(None,'Raid: Shadow Legends')
    return hwd

def gimmeAppArea(hwd):
    # Screen area of application
    screenarea = win.GetWindowRect(hwd)    
    
    return screenarea
    
def setAppFocus(hwd):
    dt = 1e-2
    try:
        # Set RAID to foreground!
        win.SetForegroundWindow(hwd); time.sleep(dt)
        if not gimmeAppFocus() == hwd: setAppFocus(hwd)
    except:
        win.ShowWindow(hwd, 6) # Minimize
        time.sleep(dt)
        win.ShowWindow(hwd, 9) # Un-minimize
        time.sleep(dt)
        setAppFocus(hwd)       # Focus app


def gimmeAppMovement(hwd, screenarea, click_loc, click_scr):
    check = False;
    
    scroi = gimmeAppArea(hwd);
    if scroi != screenarea:
        check = False        
        screenarea = scroi;                
        
    click_scr = \
        list(np.add(click_loc,[screenarea[1], screenarea[0]]).astype(int));
        
    
    return check, screenarea, click_scr
    

def gimmeAppFocus():
    hwd_foreground = win.GetForegroundWindow()
    return hwd_foreground

def gimmeColorCheck(clr, clrmin, clrmax):
    # Given minimum and maximim RGB values returns if CLR is within given 
    # range.
    
    if clr[0] >= clrmin[0] and clr[0] <= clrmax[0]: r = True
    else: r = False    
    if clr[1] >= clrmin[1] and clr[1] <= clrmax[1]: g = True
    else: g = False        
    if clr[2] >= clrmin[2] and clr[2] <= clrmax[2]: b = True
    else: b = False
    
    return r,g,b


# ------------------------------------------------------------- #
#                           PREP WORK                           #
# ------------------------------------------------------------- #


# Matchtime / iterdt is how long the script will sleep between screen-checks
# for clicking the replay button
iterdt = 100;
click_px_offset = 3;
mouse = Controller(); # Get controller for the mouse ----- #

pbarL = 32



print(' ')
print('Python: Auto-Replay RAID --------------------------- #')
print('NB: Use CTRL+C to abort the script at any time.')
print(' ')
print('      << Always inspect IMG and NFO >>')
print(' ')
print("# -------------------------------------------------- #")
print(' ')


# --- USER INPUT --- #

# Number of games/clicks input
nGames = input('#Games to play [-]: ')
nGames = int(nGames)   
# Match time input
matchtime = input('Match-time [s]: ')
matchtime = int(matchtime)


# Calc stastistics: x2 maximum error assumed
itermax = round(matchtime*nGames*3) 
expRunTime = matchtime * nGames; expRunTimeMax = expRunTime*2


# Get RAID-window
print('Searching for Raid Shadow Legends window...'); time.sleep(1)
try:
        
    hwd = gimmeAppID()              # Main window-arg    
    screenarea = gimmeAppArea(hwd)  # Screen area
    setAppFocus(hwd)                # Set RAID to foreground!
    time.sleep(1)
    
    print('Raid-window found! Continuing...')
    
except:  
    print('Raid-window not found; Aborting.')
    sys.exit('No RAID window found; application closed?')


# Image grab
img = gimmeImage(screenarea) #; plt.imshow(img)
# Image dimensions
imsz = list(img.shape)

# Returns click-location in grabbed image
click_loc, ROI = gimmeClickLocation(img)
if click_loc == 0: sys.exit('Click location in IMG is zero!');

# Convert to Y and X on screen for mouse
click_scr = \
    list( np.add(click_loc,[screenarea[1], screenarea[0]]).astype(int));


# ---------------- IMG GRAB -------------- #

# Image grab
img = gimmeImage(screenarea)

# Image dimensions
imsz = list(img.shape)

# --- Color to Click --- #
col_dt = [3, 5, 10]
coi = img[int(click_loc[0]), int(click_loc[1])];

# Color range for PIXEL-COLOR (MIN AND MAX)
clr_min = np.subtract(coi,col_dt); clr_min[clr_min<0] = 0
clr_max = np.add(coi,col_dt); clr_min[clr_max>255] = 255


# -------------------------------------
# Print NFO
# -------------------------------------


print("# -------------------------------------------------- #")
print("# ------------------     NFO       ----------------- #")
print("# -------------------------------------------------- #")
# print('Image dimensions:      '  + str(imsz))
# print('Click location>image:  '  + str(click_loc))
# print('Click location>screen: '  + str(click_scr))
# print("")
# print("RGB Values for Pixel-Color:")
# print('Click-color MIN:   '  + str(clr_min))
# print('Click-color PIXEL: '  + str(coi))
# print('Click-color MAX:   '  + str(clr_max))
# print('NB. Color of the Replay-button.')
# print("")
print(" ")
print('Maximum #iterations [-]:   {:3.2f}'.format(itermax))
print('Time per iteration  [s]:   {:3.2f}'.format(matchtime/iterdt))
print('Expected run-time   [min]: {:3.2f}'.format(expRunTime/60))
print('Maximum run-time    [min]: {:3.2f}'.format(expRunTimeMax/60))
print(" ")
print("# -------------------------------------------------- #")


# print("")
# print('Close the IMG window to continue...')
# print("")
# # Show first image and click-location
# plt.imshow(img); plt.title('ScreenGrab');
# plt.plot(int(click_loc[1]),int(click_loc[0]),'o',markersize=2, color='red')
# plt.show()

# Initial call to print 0% progress
progress.bar(0, nGames, pbarL, ['Playing','..','Done!']);    


# ------------------------------------------------------------- #
#               START LOOPING FROM HERE                         #
# ------------------------------------------------------------- #

# LOADS OF CONTAINERS
npergame = [0]*nGames  # Iterations per game
n = 0; clcks = 0; skps = 0;
n_fgd = 0; n_fgd_repeat = -1;
fgdebug_fac = 0.80; # FG debugger constant
while (n-1) < (itermax+1):
    n = n + 1; # Iterator :)
    
        
    # Check for app-movement: update screenarea and click-location
    check, screenarea, click_scr = \
        gimmeAppMovement(hwd, screenarea, click_loc, click_scr)
    
    img = gimmeImage(screenarea); # Image-grab       

    # Color of mouse-position minus a few to possibly AVOID the MOUSE-CURSOR
    # Dont want to move the mouse away constantly
    px_col = img[int(click_loc[0])-click_px_offset, \
                 int(click_loc[1])-click_px_offset]
        
    # Within color range-CHECK      
    r,g,b = gimmeColorCheck(px_col, clr_min, clr_max)

    # If within color range - click!
    if r and g and b:     
        # Set app-focussed
        # setAppFocus(hwd);
        
        # Click position in image and on screen
        mouse.position = (click_scr[1], click_scr[0]); time.sleep(10e-2)        
        time.sleep(1e-3)
        mouse.click(Button.left, 1);        
        
        
        # Statistics
        npergame[clcks] = n
        clcks = clcks + 1;
        
        # Reset counters
        n_fgd = 0; n_fgd_repeat = -1;
        
        # Update bar
        progress.bar(clcks, nGames, pbarL, ['Playing','..','Done!']); 
        
    else:
        skps = skps + 1
                
        
    # END OF GAMES! # ------ #
    if clcks >= nGames:
        print('#Iterations: ' + str(n) + ' | #Skips: ' + str(skps))
        tmpN = [0]*nGames
        for kk in range(nGames):
            if not kk == 0: tmpN[kk] = npergame[kk] - npergame[kk-1]
            else:           tmpN[kk] = npergame[kk]
                
        print('#Iterations per game [-]: ' + \
              ', '.join('{:0.2f}'.format(ii) for ii in tmpN))
        
        timepergame = np.multiply(matchtime/iterdt, tmpN)
        print('Time per game [s]: ' + \
              ', '.join('{:0.2f}'.format(ii) for ii in timepergame))
            
        print('Averages [-|min]: %3.0f | %3.2f' % \
              (np.mean(tmpN[1:]), np.mean(timepergame[1:])))
        print('\n')
        
        break; # DONE!
    
    # WHILE-LOOP-SAFETY
    if n >= itermax: 
        progress.bar(nGames, nGames, pbarL, ['Playing','..','Stopped!']); 
        print("\n # --- Reached iteration maximum. --- # \n"); 
        break

    # Wait time each iteration
    time.sleep(matchtime/iterdt)
    
    
    # n_fgd = n_fgd + 1;
    # hwd_foreground = gimmeAppFocus();  # FOREGROUND APPLICATION    
    # # Foreground Debugger Script (FGD)
    # if n_fgd >= (iterdt*fgdebug_fac):
    #     # After "fgdebug_fac" more iterations/game than expected
    #     n_fgd_repeat = n_fgd_repeat + 1
    #     print('FGD Active: ' + str(n_fgd_repeat))
    #     if ((n_fgd_repeat % 2.0) == 0): 
    #         print('Setting Raid to FG!: ' + str(n_fgd_repeat))
    #     # If #iterations/games is passed....
    #     # Try every 5 iterations....
    #         if not (hwd_foreground == hwd): 
    #             setAppFocus(hwd);  # RAID TO ACTIVE
    #             time.sleep(1)
    #             n_fgd = -1; n_fgd_repeat = -1 # Reset Foreground-debugger
    #         else: n_fgd_repeat = n_fgd_repeat - 1    
    # # If n_fgd == 0; foreground window has changed - return 2 original
    # if (n_fgd  == 0): 
    #     print('FG app back!')
    #     setAppFocus(hwd_foreground); time.sleep(0.5)      