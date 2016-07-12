# -*- coding: utf-8 -*-
"""
Created on Tue Jul 05 17:35:51 2016

@author: axelt
"""
import threading

class SignalProcessor (object):
    def __init__ (self, listenPort, sendPort):
        self.listenPort = listenPort
        self.sendPort = sendPort
        self.buffer=[]
        
        #the mne objects returned by the process command
        self.processed=[]
        print "Created!"
        
        
    def listen (self, blocksize):
        import socket
        import sys
        
        self.allData = ""        
        
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind the socket to the port
        server_address = ('localhost', self.listenPort)
        print >>sys.stderr, 'starting up on %s port %s' % server_address
        sock.bind(server_address)
        
        # Listen for incoming connections
        sock.listen(1)
        
        while True:
            # Wait for a connection
            print >>sys.stderr, 'waiting for a connection'
            connection, client_address = sock.accept()
            
            try:
                print >>sys.stderr, 'connection from', client_address
        
                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(blocksize)
                    print >>sys.stderr, 'received "%s"' % data
                    self.allData = self.allData + data
                    self.buffer.append(data)
                    
                    if data:
                        print >>sys.stderr, 'sending data back to the client'
                        connection.sendall(data)
                    else:
                        print >>sys.stderr, 'no more data from', client_address
                        return
                    
            finally:
                # Clean up the connection
                print "Closed connection"
                connection.close()
                    
    def runListen(self, blocksize):
        self.t1 = threading.Thread(target=self.listen, args=([blocksize]))
        self.t1.start()
        


    def getWorkingBuffer (self, buffersize):
        #should all past data be kept in list?
        if len(self.buffer)>=buffersize:
            #get the last n elements of the buffer where n is the buffersize parameter (order is preserved)
            workingBuffer = self.buffer[-1 * buffersize:]
            return workingBuffer
        return []
            
    def runProcessSignal (self, buffersize = 8, interval = 0.5):
        t1 = threading.Thread(target=self.processSignal, args=([buffersize, interval]))
        t1.start()       

            
    def processSignal (self, buffersize, interval):
        import time 
        print "Beginning run"
        
        #run until there is no more data being streamed
        while self.t1.isAlive():
            
            time.sleep(interval)
            _buffer = self.getWorkingBuffer(buffersize)
            #if buffer is full enough
            if _buffer:
                print "Working on buffer :"
                print _buffer
                result = self.lowLevelSignalProcesssing(_buffer)
                transmissableResult = self.transformProcessedSignal(result)
                
                #add the processed signal to the list of processed signals
                self.processed.append(transmissableResult)
                #@TODO maybe add a timestamp?     
            
        
        
        
    def lowLevelSignalProcesssing (self, _buffer):
        #@TODO
        #use MNE to process the contents of the buffer
        return _buffer[0]
        
    def transformProcessedSignal (self, proc):
        #@TODO
        #take the mne object and extract the data needed for visualization
        return proc
        
        
        
    def streamData (self, interval, blocksize):
        
        import socket
        import time 
        self.sock = socket.create_connection(('localhost', self.sendPort))
        while self.t1.is_alive():
            while self.processed:
                self.sendMessage(self.processed.pop(), blocksize)
            time.sleep(interval)
        self.sock.close()
    
    def sendMessage (self, message, blocksize):
        
        import sys
        
        # Send data
        self.sock.sendall(message)
    
        amount_received = 0
        amount_expected = len(message)
        
        while amount_received < amount_expected:
            data = self.sock.recv(blocksize)
            amount_received += len(data)
            print >>sys.stderr, 'received "%s"' % data
            
    def runStreamResults(self, interval = 0.5, blocksize = 32):
        t1 = threading.Thread(target=self.streamData, args=([interval,blocksize]))
        t1.start()
        
        
        
        
        
        
        
        
        
        
        
        
        
