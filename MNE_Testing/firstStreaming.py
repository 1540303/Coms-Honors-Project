#Core visualization and signal processing package
import mne

#Sample files used for testing and demo purposes
from mne.datasets import somato

#Allow for streaming and visualization threads
import threading

#Facilitates time comparissons
import time

#Used to create GIF
import imageio

#MNE currently has a warning that outputs to standard out (very strange)
#This is used to mask it
import warnings
warnings.filterwarnings("ignore")

from contextlib import contextmanager
import sys, os

from contextlib import contextmanager
import sys, os

import shutil

#=======================================================
#===========SUPPRESSION=================================
"""
* Suppresses the default output of the MNE toolbox which outputs to std out
* for no good reason.
* @return returns no value, rather that some output
"""
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
#==========SET VARIABLES================================
#number of images generated in this visualisation
count=0
#array of images from current visualization call
images = []
#stremaing thread
t1 = -1
#visualization thread
t2 = -1

"""
* Split data into chunks of a size determined by the user
* @param raw - the raw data input (eeg/meg file)
* @param interval - the desired size of each chunk in seconds
* @return - the split data as a list
"""
def splitRaw(raw, interval = 50):
    raws=[]
    with suppress_stdout():
        for i in range (0, int(raw._times[-1]/interval)):
                raws.append(raw.crop(interval * i, interval * (i+1)))
    return raws

"""
* Create a topomap from a supplied raw file
* @param raw - an mne interval object
* @param bands - labelled band intervals to be used for the visualization
* @return returns the created topomap (a plt object)
"""
def drawTopo (raw, bands=None):
    # standard filtering
    picks = mne.pick_types(raw.info, meg=True, exclude='bads')  

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
    
    topomap = epochs.plot_psd_topomap(ch_type='grad', normalize=True, bands=bands)
    return topomap

"""
* Saves a plt object as an image
* @param image - the plt object to save
* @param value - the name of the image
* @param folder - the folder into which the image should be saved
"""
def saveImage (image,value=0, folder=""):
    fig = image
    print "folder is " + str(folder)
    name = "figs/" + folder +"/fig" + str(value) + ".png"
    fig.savefig(name)        

"""
* Function, run as a thread, that empties a source mne interval object into a
* destination interval object. Run in conjunction with beginVisualizing().
* @param raw - the source mne interval object to be emptied
* @param raw2 - the empty interval object to be filled and visualized
* @param interval - the delay between the transfer of each second from raw to
* raw2
"""
def beginStreaming (raw, raw2, interval = 0.5):
    for i in range (0, int(raw._times[-1])):
        #send at second intervals
        with suppress_stdout():
            toSend = raw.crop(i,i+1)
        raw2.append(toSend)
        time.sleep(interval)

"""
* Function, run as a thread, that visualized data from a growing mne interval
* object
* @param raw - the grawing mne interval object that is being expanded by the
* concurrent beginStreaming() thread
* @param images - the list of plt object contained previously created plots
* @param bands - labelled band intervals to be used for the visualization
* @param interval - the delay between the transfer of each second from raw to
* raw2
* @param initial - the initial delay before the thread begins visualizing
* @param buffersize - the number of entries from raw that are used for 
* visualization
* folder - the subfolder within the /figs folder in which the image is to be
* saved
"""
def beginVisualizing (raw, images, bands=None, interval = 5, initial=20, bufferSize = 100, folder=""):
    # sleep for the initial specified interval
    time.sleep(initial)
    global count
    # visualize while data is being streamed
    while t1.is_alive():
        # only attempt visualization if at least [bufferSize] worth of data has
        # been streamed
        if len(raw)>bufferSize:
            # reading at bufferSize measurements in the past
            firstTime = raw.times[-1*bufferSize]
            # most recent reading
            lastTime = raw.times[-1]
        
            try:
                # extract the interval of buffersize
                tempRaw = raw.crop(firstTime, lastTime)
            except:
                print "End of file..."
            try:
                # create the plt object of the topomap
                image = drawTopo(tempRaw,bands)
                # store the plt object of the topomap
                images.append(image)
                # save the image in an appropriate folder
                saveImage(image, count, folder)
                # store the image in the temporary folder that the browser
                # reads from
                saveImage(image, count, "temp")
                #increment the number of successfully generated topomaps
                count = count + 1
                
            except: 
                x=0
        #wait the specified amount of time
        time.sleep(interval)

"""
* Delete all files from a specified directory
* @param directory - the directory to be emptied
"""
def emptyDir (directory):
    filelist = [f for f in os.listdir(".")]
    for f in filelist:
        os.remove(f)

"""
* Main method for reading an fif source file and creating the streaming 
* visualization
* @param bands - labelled band intervals to be used for the visualization
* @param reduceSize - prevents visualization of the whole file (often 20+ 
* minutes)
* @param folder - the subfolder within the /figs folder in which the image is to be
* saved
* @return all topomaps generated in this run
"""  
def visualize(bands=None, folder="", reduceSize = True):
    #emptyDir("figs/temp")
    
    print 1
    data_path = somato.data_path()
    raw_fname = data_path + '/MEG/somato/sef_raw_sss.fif'
    
    # read the raw data
    raw = mne.io.read_raw_fif(raw_fname)
     
    
    
    print 2
    global images
    #reduce the size of the data file for quick testing if specified
    if reduceSize:
        splitData = splitRaw(raw, 100) 
        sourceData=splitData[0]
    else:
        sourceData=raw
    
    #creates an mne interval object with no measurements inside
    streamedData = sourceData.crop(0,0)
    
    print folder

    print 3
    global t1
    streamInterval = 1
    # thread streams data from [sourceData] to [streamedData]
    t1 = threading.Thread(target=beginStreaming, args=([sourceData,streamedData,streamInterval]))
    t1.start()
         
    
    print 4
    global t2
    visInterval = 1
    initial = 1
    bufferSize = 5000
    # thread visualizes the contents of the streamed data interval object
    t2 = threading.Thread(target=beginVisualizing, args=([streamedData, images, bands, visInterval, initial, bufferSize, folder]))
    t2.start()     

    
    print 5
    # do not continue until both threads have terminated
    t1.join()
    t2.join()
    
    # reset the number of figures generated in the current stream
    global count
    count = 0

    print ("Done")
    return images

"""
* Creates a .gif file from the .png contents of a folder
* @param folder - the first level folder
* @param subfolder - the second level folder
"""
def createGif (folder='figs', subfolder=""):
    f=folder + "/" + subfolder + "/"
    with imageio.get_writer(f+'movie.gif', mode='I') as writer:
        for file in os.listdir(f):
            if file.endswith(".png"):
                filename = f + str(file)
                print filename
                image = imageio.imread(filename)
                writer.append_data(image)

"""
* Creates a set of fixed intervals (default between 0.0hz and 45.0hz). Used as 
* part of testing
* @param minVal - the lowest expected measured activity
* @param maxVal - the highest measured expected activity
* @param numSteps - the number of discrete bands to create (each band is used
* to test a visualization with that many topomaps)
* @return a list containing the specified band ranges
"""
def createBandRange(minVal=0.0, maxVal=45.0, numSteps=4):
    interval = (maxVal-minVal)/numSteps
    l = [x*interval for x in range (1, numSteps+1)]
    li = [(x-interval,x,str(x)) for x in l]
    return li

"""
* funtion used to test creation with various parameters
* @param maxBandSize - the number of bands [1-maxBandSize] to make and visualize
* This is a time intensive function and should not be used with maxBandSize>10
""" 
def testing(maxBandSize=5):
    print "TESTING"
    bands=[]
    for i in range (1, maxBandSize+1):
        band = createBandRange(numSteps=i)
        bands.append(band)
    
    for band in bands:
        visualize(bands=band, folder="samples_"+str(len(band)))
    
#16 images args=([raw2, images, 1, 15, 5000]
BANDS = [(0, 4, 'Delta'), (4, 8, 'Theta'), (8, 12, 'Alpha'), (12, 30, 'Beta'), (30, 45, 'Gamma')]

#31 images args=([raw2, images, 1, 15, 5000]
#BANDS = [(0, 45, 'All')]
         
#19 images args=([raw2, images, 1, 15, 5000]
#BANDS = [(0, 4, 'Delta'), (4, 8, 'Theta'), (8, 12, 'Alpha'), (12, 40, 'Beta')]
         



start_time = time.time()

with suppress_stdout():
    print "starting"
    images = visualize(BANDS, folder = "samples_"+str(len(BANDS)))    
print ("DONE")
print("--- %s seconds ---" % (time.time() - start_time))


"""
with suppress_stdout():
    print "starting"
    testing(maxBandSize=1)
"""

for i in range (1, 10):
    createGif('figs', "samples_"+str(i))