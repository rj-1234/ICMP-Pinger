import socket
import os
import sys
import struct
import time
import select
import binascii  

ICMP_ECHO_REQUEST = 8 

def checksum(string):
    string = bytearray(string) 
    csum = 0
    countTo = (len(string) / 2) * 2
    
    count = 0
    while count < countTo:
        thisVal = (string[count+1] * 256 + string[count])        
        csum = csum + thisVal        
        csum = csum & 0xffffffff       
        count = count + 2

    if countTo < len(string):
        csum = csum + ord(string[len(string) - 1])
        csum = csum & 0xffffffff
        
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff   
    answer = answer >> 8 | (answer << 8 & 0xff00)    
    return answer

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while 1:        
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect) 
        if whatReady[0] == []: # Timeout
            return "Request timed out."
        
        timeReceived = time.time()        
        recPacket, addr = mySocket.recvfrom(1024)
       
        icmpHeader = recPacket[20:28]
        req_type, code, mychecksum, r_id, r_seq = struct.unpack('bbHHh',icmpHeader)

        if type != 8 and ID == r_id:
            bytesInDouble = struct.calcsize('d')
            timeData = struct.unpack('d', recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeData
        else:
            return "Different ID"     
        
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."        

def sendOnePing(mySocket, destAddr, ID):
    
    myChecksum = 0
    
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)    
    data = struct.pack("d", time.time())        
    myChecksum = checksum(header + data)
        
    if sys.platform == 'darwin':
        myChecksum = socket.htons(myChecksum) & 0xffff      
    else:
        myChecksum = socket.htons(myChecksum)    
    
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)     
    packet = header + data
 
    mySocket.sendto(packet, (destAddr, 1)) 
     
def doOnePing(destAddr, timeout):    
    icmp = socket.getprotobyname("icmp")     
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    myID = os.getpid() & 0xFFFF  
    sendOnePing(mySocket, destAddr, myID) 
    delay = receiveOnePing(mySocket, myID, timeout, destAddr) 
    
    mySocket.close()    
    return delay

def ping(host, timeout=1):
    
    dest = socket.gethostbyname(host)
    print ("Pinging " + dest + " using Python:")
    print( "")
    
    while 1 :
        delay = doOnePing(dest, timeout)
        print (delay)
        time.sleep(1)
    return delay

#ping("www.google.com")
#ping("www.auditonline.gov.in")
#ping("www.australia.gov.au")
ping("www.eurid.eu")