import numpy as np
import matplotlib.pyplot as plt

import mne
from mne.time_frequency import tfr_morlet, psd_multitaper
from mne.datasets import somato
import threading
import time



import warnings
warnings.filterwarnings("ignore")




from contextlib import contextmanager
import sys, os

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout



#=======================================================
#==========SET PARAMETERS===============================

from contextlib import contextmanager
import sys, os


def splitRaw(raw, interval = 50):
    raws=[]
    with suppress_stdout():
        for i in range (0, int(raw._times[-1]/interval)):
                raws.append(raw.crop(interval * i, interval * (i+1)))
    return raws

def drawTopo (raw):
    #standard filtering
    picks = mne.pick_types(raw.info, meg=True, exclude='bads')  
    
    #time segment wanted
    t_idx = raw.time_as_index([10., 20.])  
    data, times = raw[picks, t_idx[0]:t_idx[1]] 
    
    
    events = mne.find_events(raw, stim_channel='STI 014')
    
    
    
    # picks MEG gradiometers
    picks = mne.pick_types(raw.info, meg='grad', eeg=False, eog=True, stim=False)
    
    
    # Construct Epochs
    event_id, tmin, tmax = 1, -1., 3.
    baseline = (None, 0)
    epochs = mne.Epochs(raw, events, event_id, tmin, tmax, picks=picks,
                        baseline=baseline, reject=dict(grad=4000e-13, eog=350e-6),
                        preload=True)
    
    
    epochs.resample(150., npad='auto')  # resample to reduce computation time
    
    
    #=======================================================
    #==========PLOT EPOCHS==================================
    #epochs.plot_psd(fmin=2., fmax=40.)
    
    
    #=======================================================
    #==========TOPOGRAPHICAL MAPS===========================
    epochs.plot_psd_topomap(ch_type='grad', normalize=True)
    
      
    
    
def beginStreaming (raw, raw2, interval = 0.5):
    for i in range (0, int(raw._times[-1])):
        #send at second intervals
        with suppress_stdout():
            toSend = raw.crop(i,i+1)
        raw2.append(toSend)
        time.sleep(interval)

def beginVisualizing (raw, interval = 5, initial=20, bufferSize = 100):
    time.sleep(initial)
    while t1.is_alive():
        
        if len(raw)>bufferSize:
            firstTime = raw.times[-1*bufferSize]
            lastTime = raw.times[-1]
        
            try:
                tempRaw = raw.crop(firstTime, lastTime)
            except:
                print "End of file..."
            try:
                drawTopo(tempRaw)
            except: 
                x=0
        time.sleep(interval)
        


     
#WORKS WITH ANY .fif FILE!
#@TODO replace with actual path
data_path = somato.data_path()
raw_fname = data_path + '/MEG/somato/sef_raw_sss.fif'
data_path = 'C:/Anaconda2/Lib/site-packages/examples/mne-testing-data-master'

# Setup for reading the raw data
raw = mne.io.read_raw_fif(raw_fname)
a = splitRaw(raw, 100)  


raw=a[0]
with suppress_stdout():
    raw2 = raw.crop(0,0)



t1 = threading.Thread(target=beginStreaming, args=([raw,raw2,1]))
t1.start()
     

with suppress_stdout():
    t2 = threading.Thread(target=beginVisualizing, args=([raw2,1, 20, 5000]))
    t2.start()     


t1.join()
t2.join()
print ("Done")

