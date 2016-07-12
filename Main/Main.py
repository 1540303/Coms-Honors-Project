# -*- coding: utf-8 -*-
"""
THIS CLASS CONTROLS THE OVERALL COMMUNICATION BETWEEN THE COMPONENETS OF THE EEG VISUALIZATION SYSTEM
"""

"""
IMPORTS
"""
import DataStreamer as ds
import SignalProcessor as sp
import ImageVisualizer as iv
"""
BASIC VARAIBLES
"""
ports = [10000, 10001, 10002]

#USED PRIMARILY FOR TESTING PURPOSES
fromFromFile = True
FILENAME = "Data/noise.txt"
BLOCKSIZE = 32
PROCESSINGBUFFERSIZE = 8
"""
CREATE THE WEBSOCKET MODULES
"""
#CREATE THE DATA STREAMER
streamer = ds.DataStreamer(filename = FILENAME, port = ports[0])

#CREATE THE SIGNAL PROCESSOR
processor = sp.SignalProcessor(listenPort = ports[0], sendPort = ports[1])

#CREATE THE VISUALIZATION MODULE
visualizer = iv.ImageVisualizer(listenPort = ports[1])

"""
FEED EEG DATA FROM THE FILE RAW FILE
"""
#BEGIN STREAMING THE CONTENTS OF THE FILE
streamer.run(interval = 0.05, blocksize = BLOCKSIZE)


"""
SIGNAL PROCESSING
"""
#LISTEN FOR LINES FROM THE DATA STREAMER (OR ANYTHING ELSE WORKING ON THE SAME PORTS)
processor.runListen(blocksize = BLOCKSIZE)

#USE THE SIGNAL PROCESSING CAPABILITIES OF MNE TO INTERPRET THE STREAMING DATA
processor.runProcessSignal(buffersize = PROCESSINGBUFFERSIZE, interval = 0.5)


"""
VISUALIZATION
"""
visualizer.runListen(blocksize=BLOCKSIZE)


#TRANSMIT THE PROCESSED DATA TO THE VISUALIZER
processor.runStreamResults(interval = 0.5, blocksize = BLOCKSIZE)

#BEGIN ACTUAL VISUALIZATION



#for debugging purposes
visualizer.t1.join()
print "============================="
print "Vis"
print visualizer.buffer
print "============================="






def createNoise (filename="Data/noise.txt", length=2000, lineLength=31):
    import numpy as np
    data = np.random.rand(length)
    data = np.floor(data * 26 + 65)
    print data
    stra = ""
    for i in range(0, len(data)):
        stra = stra + chr(int(data[i]))
        if (i+1)%lineLength==0:
            stra=stra+"\n"            
    print stra
    
    f = open(filename,'w')
    f.write(stra) # python will convert \n to os.linesep
    f.close() # you can omit in most cases as the destructor will call it
