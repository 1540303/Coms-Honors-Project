import numpy as np
import matplotlib.pyplot as plt

import mne
from mne.time_frequency import tfr_morlet, psd_multitaper
from mne.datasets import somato

#=======================================================
#==========SET PARAMETERS===============================


def splitRaw(raw, interval = 50):
    raws=[]
    for i in range (0, int(raw._times[-1]/interval)):
        print "--> " + str(interval * i)
        print "-->" + str(interval * (i+1))
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
#WORKS WITH ANY .fif FILE!
#@TODO replace with actual path
data_path = somato.data_path()
raw_fname = data_path + '/MEG/somato/sef_raw_sss.fif'
data_path = 'C:/Anaconda2/Lib/site-packages/examples/mne-testing-data-master'

# Setup for reading the raw data
raw = mne.io.read_raw_fif(raw_fname)

a = splitRaw(raw, 50)

for i in range (0, len(a)):
    drawTopo(a[i])    

"""
"""