# This is server code to send video and audio frames over UDP/TCP

import os
from time import sleep
try:
    import cv2, imutils, socket
    import time
    import base64
    import wave, pickle, struct
    import sys
    import queue
    from concurrent.futures import ThreadPoolExecutor
except:
    print("Alguns pacotes precisam ser instalados!\n Favor checar novamente os pacotes instalados!\n")
    os._exit(1)

def AudioBufferCreate():
    command = "del /f temp.wav"
    os.system(command)
    command = "ffmpeg -i " + filename + " -ab 160k -ac 2 -ar 44100 -vn temp.wav"
    os.system(command)

def VideoBufferCreate():
    WIDTH=400
    while(vid.isOpened()):
        try:
            _,frame = vid.read()
            frame = imutils.resize(frame,width=WIDTH)
            videoBuffer.put(frame)
        except:
            os._exit(1)
    print('Connection to', cAddress, 'is closed...')
    vid.release()

def VideoStreaming():
    #sleep(1.5)
    global vidTS
    fps,st,frames_to_count,cnt = (0,0,1,0)
    cv2.namedWindow(('Transmitindo ' + filename + '...'))        
    cv2.moveWindow(('Transmitindo ' + filename + '...'), 10,30) 
    while True:
        frame = videoBuffer.get()
        encoded,buffer = cv2.imencode('.jpeg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
        frameData = base64.b64encode(buffer)
        serverSocket.sendto(frameData,cAddress)

        frame = cv2.putText(frame,'FPS: '+str(round(fps,1)),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
        if cnt == frames_to_count:
            try:
                fps = (frames_to_count/(time.time()-st))
                st=time.time()
                cnt=0
                if fps>vidFPS:
                    vidTS+=0.01
                elif fps<vidFPS:
                    vidTS-=0.01
                else:
                    pass
            except:
                pass
        cnt+=1
        
        cv2.imshow(('Transmitindo ' + filename + '...'), frame)
        key = cv2.waitKey(int(1000*vidTS)) & 0xFF	
        if key == ord('q'):
            os._exit(1)	
                

def AudioStreaming():
    audioSocket = socket.socket()
    audioSocket.bind((serverIP, (serverPort-1)))

    audioSocket.listen(5)
    CHUNK = 1024
    wf = wave.open("temp.wav", 'rb')

    clientSocket,addr = audioSocket.accept()

    while True:
        if clientSocket:
            while True:
                data = wf.readframes(CHUNK)
                a = pickle.dumps(data)
                audioData = struct.pack("Q",len(a))+a
                clientSocket.sendall(audioData)



videoBuffer = queue.Queue(maxsize=10)
BUFFSIZE = 65536
serverIP = sys.argv[1]
serverPort = 8081

serverSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
serverSocket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFFSIZE)
hostname = socket.gethostname()

sAddress = (serverIP,serverPort)
serverSocket.bind(sAddress)
print('The server started at',sAddress)

while True:
    msg, cAddress = serverSocket.recvfrom(BUFFSIZE)
    print(msg)
    filen = msg.decode("utf-8")
    print('Conexao com', cAddress, 'estabelecida...\n')
    filename = str(filen)
    try:
        print(filename)

        AudioBufferCreate()

        vid = cv2.VideoCapture(filename)
        vidFPS = vid.get(cv2.CAP_PROP_FPS)
        global vidTS
        vidTS = (0.5/vidFPS)
        print('FPS:',vidFPS,vidTS)
        vidTNF = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = float(vidTNF) / float(vidFPS)
        d = vid.get(cv2.CAP_PROP_POS_MSEC)
        print(duration,d)
            
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(AudioStreaming)
            executor.submit(VideoBufferCreate)
            executor.submit(VideoStreaming)
    except:
        msg = "Arquivo " + filename + " não encontrado!"
        msg = msg.decode("utf-8")
        serverSocket.sendto(msg,(serverIP,serverPort))
