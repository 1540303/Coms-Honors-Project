import threading

class ImageVisualizer (object):
    def __init__ (self, listenPort):
        self.listenPort = listenPort
        self.buffer=[]
        print "Created!"
        
        
    def listen (self, blocksize):
        import socket
        import sys      
        
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
            print "----------------------------------------------"
            try:
                print >>sys.stderr, 'connection from', client_address
        
                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(blocksize)
                    print >>sys.stderr, 'received "%s"' % data
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
        