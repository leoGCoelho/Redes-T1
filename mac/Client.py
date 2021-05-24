# Nome: Leonardo Gularte Coelho

import threading, time, os, sys, base64, socket
try:
    import numpy as np
    import cv2
    import pyaudio, pickle, struct
except:
    print("Alguns pacotes precisam ser instalados!\n Favor checar novamente os pacotes instalados!\n")
    os._exit(1)


def VideoStreaming():
	cv2.namedWindow(('Recebendo ' + sys.argv[1] + '...'))        
	cv2.moveWindow(('Recebendo ' + sys.argv[1] + '...'), 10,360) 
	fps,st,ftc,cnt = (0,0,20,0)								# dados de contagem dos frames


	while True:
		package,_ = clientSocket.recvfrom(BUFFSIZE)			# recebe os frames do video via UDP
		data = base64.b64decode(package,' /')
		npdata = np.fromstring(data,dtype=np.uint8)

		frame = cv2.imdecode(npdata,1)						# decodifica imagem recebida		
		#frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)		# legenda com os frames da reproducao
		cv2.imshow(('Recebendo ' + sys.argv[1] + '...'),frame)	# mostra frame na tela
		key = cv2.waitKey(1) & 0xFF
		
		if key == ord('q'):									# caso 'q' seja apertado, fecha video
			clientSocket.close()
			os._exit(1)
			break

		if cnt == ftc:										# sincroniza velocidade de frames do video
			try:
				fps = round(ftc/(time.time()-st),1)
				st = time.time()
				cnt = 0
			except:
				pass
		cnt+=1


# Recebendo o arquivo WAV via TCP e reproduz em paralelo
def AudioStreaming():
	# abre um canal para reproducao do audio
	audioBuffer = pyaudio.PyAudio()
	CHUNK = 1024
	stream = audioBuffer.open(format=audioBuffer.get_format_from_width(2), channels=2, rate=44100, output=True, frames_per_buffer=CHUNK)
					
	clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sAddress = (clientIP,clientPort-1)

	clientSocket.connect(sAddress)								# abre conexao com o servidor para receber os dados via TCP
	print("Conexao com", sAddress, "estabelecida...\n")
	data = b""
	dataSize = struct.calcsize("Q")

	while True:													# reproduz dados recebidos do servidor
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

			frameData = data[:msgSize]
			data  = data[msgSize:]
			frame = pickle.loads(frameData)
			stream.write(frame)

		except:
			break

	clientSocket.close()
	print('Audio closed',BREAK)
	os._exit(1)


# Download de arquivos via TCP
def RecvFromServer():
	recvSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	recvSocket.connect((clientIP,clientPort-1))

	with open(sys.argv[3], 'wb') as filedata:
		print("Recebendo",sys.argv[3],'...')
		while 1:
			data = recvSocket.recv(1000000)
			if not data:
				break
			filedata.write(data)


# Upload de arquivos via TCP
def SendToServer():
	recvSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	recvSocket.connect((clientIP,clientPort-1))

	with open(sys.argv[3], 'rb') as filedata:                      # abre arquivo desejado
		print("Enviando",sys.argv[3],'...')
		for data in filedata.readlines():
			recvSocket.send(data)                             # envia linhas do arquivo para o cliente




# Main
# variaveis globais
BUFFSIZE = 65536
BREAK = False

clientIP = sys.argv[1]
clientPort = 8081
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
clientSocket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFFSIZE)
hostname = socket.gethostname()

# dados de conexao
if(sys.argv[2] == '-v'):											# caso de streaming de arquivo
	try:
		msg = 'VIEW//'+ sys.argv[3]
		msg = str.encode(msg)								# codifica endereco do arquivo
	except:
		print('Por favor adicione o nome do arquivo aos argumentos\n')
		os._exit(1)

	clientSocket.sendto(msg,(clientIP,clientPort))					# realiza conexao entre cliente e o servidor, enviando endereco do arquivo

	try:
		if('.mp4' in sys.argv[3]):									# se arquivo for um video
			t1 = threading.Thread(target=AudioStreaming, args=())
			t1.start()												# paraleliza audio para reproduzir junto aos frames

			VideoStreaming()										# reproduz video

		elif('.wav' in sys.argv[3]):								# caso o arquivo um audio
			AudioStreaming()										# recebe os dados via TCP

		else:														# caso seja outro tipo de arquivo, da erro
			print('Formato invalido!')							

	except:
		print('Erro durante a conexão. Por favor tente novamente!\n')	# caso o arquivo nao esteja no servidor, da erro
		os._exit(1)

elif(sys.argv[2] == '-d'):											# caso de download de arquivo
	try:
		msg = 'GET//'+ sys.argv[3]
		msg = str.encode(msg)								# codifica endereco do arquivo
	except:
		print('Por favor adicione o nome do arquivo aos argumentos\n')
		os._exit(1)

	clientSocket.sendto(msg,(clientIP,clientPort))					# realiza conexao entre cliente e o servidor, enviando endereco do arquivo

	RecvFromServer()
	print(sys.argv[3], 'recebido com sucesso!\n')


elif(sys.argv[2] == '-u'):											# caso de download de arquivo
	try:
		msg = 'POST//'+ sys.argv[3]
		msg = str.encode(msg)								# codifica endereco do arquivo
	except:
		print('Por favor adicione o nome do arquivo aos argumentos\n')
		os._exit(1)

	clientSocket.sendto(msg,(clientIP,clientPort))					# realiza conexao entre cliente e o servidor, enviando endereco do arquivo

	SendToServer()
	print(sys.argv[3], 'recebido com sucesso!\n')