import os
import sys
try: 
    import cv2, imutils, socket
    import numpy as np
    import time
    import base64
except:
    os.system('pip install -r requirements.txt')
    import cv2, imutils, socket
    import numpy as np
    import time
    import base64

BUFFSIZE = 65536
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFSIZE)

hostname = socket.gethostname()
try:
    hostip = sys.argv[1] #'192.168.1.65' #socket.gethostbyname(hostname)
except:
    hostip = '192.168.1.65' #meu IP
port = 8001
#print("Connected to =>", (hostip+':'+str(port)), '\n')

sAddress = (hostip, port)
print('Connected to ', sAddress, '...')

msg = b'Ola mundo!'
clientSocket.sendto(msg, sAddress)