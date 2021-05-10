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
#print("Address =>", (hostip+':'+str(port)), '\n')

sAddress = (hostip, port)
serverSocket.bind(sAddress)
print('Server running at', sAddress, '...')

fps, st, framesToCount, cnt = (0,0,20,0)


while True:
    msg, cAddress = serverSocket.recvfrom(BUFFSIZE)
    print('GOT connection from', cAddress)
    print(msg)

    try:
        if('.mp4' in msg):
            filename = cv2.VideoCapture(msg)
            WIDTH=400
            while(filename.isOpened()):
                _,frame = filename.read()
                frame = imutils.resize(frame, width=WIDTH)
                encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY,80])
                message = base64.b64encode(buffer)

                serverSocket.sendto(message, cAddress)
                frame = cv2.putText(frame, ('FPS: '+str(fps)), (10,40), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow('TRANSMITTING VIDEO...',frame)
                key = cv2.waitKey(1) & 0xFF
                if (key == ord('q')):
                    print("Server stopped\n")
                    serverSocket.close()
                    break
                if cnt == framesToCount:
                    try:
                        fps = round(framesToCount / (time.time() - st))
                        st = time.time()
                        cnt = 0
                    except:
                        pass
                cnt+=1
    except:
        msg = 'File not found!\n'
        clientSocket.sendto(msg, sAddress)