# Welcome to PyShine
# This is client code to receive video and audio frames over UDP/TCP

import threading, time, os, sys, base64, socket
try:
    import numpy as np
    import cv2
    import pyaudio, pickle, struct
except:
    print("Alguns pacotes precisam ser instalados!\n Favor checar novamente os pacotes instalados!\n")
    os._exit(1)


def AudioStreaming():
	audioBuffer = pyaudio.PyAudio()
	CHUNK = 1024
	stream = audioBuffer.open(format=audioBuffer.get_format_from_width(2), channels=2, rate=44100, output=True, frames_per_buffer=CHUNK)
					
	# create socket
	clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sAddress = (clientIP,clientPort-1)

	clientSocket.connect(sAddress) 
	print("Conexao com", sAddress, "estabelecida...\n")
	data = b""
	dataSize = struct.calcsize("Q")
	
	while True:
		try:
			while len(data) < dataSize:
				package = clientSocket.recv(4*1024)
				if not package: 
					break
				data += package

			packageSize = data[:dataSize]
			data = data[dataSize:]
			msgSize = struct.unpack("Q",packageSize)[0]

			while len(data) < msgSize:
				data += clientSocket.recv(4*1024)

			frame_data = data[:msgSize]
			data  = data[msgSize:]
			frame = pickle.loads(frame_data)
			stream.write(frame)

		except:
			break

	clientSocket.close()
	print('Audio closed',BREAK)
	os._exit(1)



BUFFSIZE = 65536
BREAK = False

clientSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
clientSocket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFFSIZE)
hostname = socket.gethostname()

clientIP = sys.argv[1]
clientPort = 8081

try:
    msg = str.encode(sys.argv[2])
except:
    print('Please add filename to arguments\n')
    os._exit(1)

clientSocket.sendto(msg,(clientIP,clientPort))

try:
	if('.mp4' in sys.argv[2]):
		t1 = threading.Thread(target=AudioStreaming, args=())
		t1.start()

		cv2.namedWindow(('Recebendo ' + sys.argv[1] + '...'))        
		cv2.moveWindow(('Recebendo ' + sys.argv[1] + '...'), 10,360) 
		fps,st,ftc,cnt = (0,0,20,0)


		while True:
			package,_ = clientSocket.recvfrom(BUFFSIZE)
			data = base64.b64decode(package,' /')
			npdata = np.fromstring(data,dtype=np.uint8)

			frame = cv2.imdecode(npdata,1)
			frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
			cv2.imshow("RECEIVING VIDEO",frame)
			key = cv2.waitKey(1) & 0xFF
			
			if key == ord('q'):
				clientSocket.close()
				os._exit(1)
				break

			if cnt == ftc:
				try:
					fps = round(ftc/(time.time()-st),1)
					st = time.time()
					cnt = 0
				except:
					pass
			cnt+=1

	elif('.wav' in sys.argv[2]):
		AudioStreaming()

	else:
		print('Formato invalido!')

except:
	print('Erro durante a conexão. Por favor tente novamente!\n')
	os._exit(1)