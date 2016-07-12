# -*- coding: utf-8 -*-
"""
Created on Tue Jul 05 12:28:23 2016

@author: axelt
"""
import threading

class DataStreamer (object):
    def __init__ (self, filename, port):
        print "CREATING DATA STREAMER ON PORT " + str(port)
        self.destinationPort = port
        self.filename = filename
        self.readFile()
        
    def readFile (self):
        with open (self.filename, "r") as myfile:
            self.data=myfile.readlines()
            
    def streamData (self, interval, blocksize):
        
        import socket
        import time 
        self.sock = socket.create_connection(('localhost', self.destinationPort))
        for line in self.data:
            self.sendMessage(line, blocksize)
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
            
    def run(self, interval, blocksize):
        t1 = threading.Thread(target=self.streamData, args=([interval,blocksize]))
        t1.start()
        