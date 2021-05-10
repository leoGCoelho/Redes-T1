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
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFSIZE)

hostname = socket.gethostname()
try:
    hostip = sys.argv[1] #'192.168.1.65' #socket.gethostbyname(hostname)
except:
    hostip = '192.168.1.65' #meu IP
port = 8001
#print("Address:  =>", (hostip+':'+str(port)), '\n')

sAddress = (hostip, port)
serverSocket.bind(sAddress)
print('Server running at', sAddress, '...')

vid = cv2.VideoCapture('db\videos\tres_espias_demais.mp4')
fps, st, framesToCount, cnt = (0,0,20,0)


while True:
    msg, cAddress = serverSocket.recvfrom(BUFFSIZE)
    print('GOT connection from', cAddress)
    print(msg)