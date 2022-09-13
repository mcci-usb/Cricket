##Client

import socket
import sys
import json

#vars
connected = False

#connect to server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.1.163',8888))
connected = True

while connected == True:
    #wait for server commands to do things, now we will just display things
    data = client_socket.recv(1024)     
    cmd = json.loads(data) #we now only expect json    
    if(cmd['type'] == 'bet'):
        bet = cmd['value']
        print('betting is: '+bet)
    elif (cmd['type'] == 'result'):        
        print('winner is: '+str(cmd['winner']))
        print('payout is: '+str(cmd['payout']))