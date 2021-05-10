import os
import sys
try: 
    import cv2, imutils, socket
    import numpy as np
    import time
    import base64
except:
    os.system('pip3 install -r requirements.txt')
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
print('Connected to ', sAddress, '...\n')

try:
    msg = str.encode(argv[2])
except:
    print('Please add filename to arguments\n')
    exit()

clientSocket.sendto(msg, sAddress)
fps, st, framesToCount, cnt = (0,0,20,0)

while True:
    if('.mp4' in argv[2]):
        packet,_ = clientSocket.recvfrom(BUFFSIZE)
        data = base64.b64decode(packet, ' /')
        npdata = np.fromstring(data, dtype=np.uint8)
        frame = cv2.imdecode(npdata, 1)

        frame = cv2.putText(frame, ('FPS: '+str(fps)), (10,40), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow('RECEIVING VIDEO...', frame)
        key = cv2.waitKey(1) & 0xFF
        if(key == ord('q')):
            print("Client stopped\n")
            clientSocket.close()
            break
        if cnt == framesToCount:
            try:
                fps = round(framesToCount / (time.time() - st))
                st = time.time()
                cnt = 0
            except:
                pass
            cnt+=1

    else:
        msg, cAddress = clientSocket.recvfrom(BUFFSIZE)
        print(msg)