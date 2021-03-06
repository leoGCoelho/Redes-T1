# Nome: Leonardo Gularte Coelho

import os, sys, time, base64,socket
from time import sleep
try:
    import cv2, imutils
    import wave, pickle, struct
    import queue
    from concurrent.futures import ThreadPoolExecutor
    from pydub import AudioSegment
except:
    print("Alguns pacotes precisam ser instalados!\n Favor checar novamente os pacotes instalados!\n")
    os._exit(1)


# Convertendo faixa de audio em um arquivo temporario WAV
def AudioBufferCreate():
    command = "rm temp.wav"
    os.system(command)
    command = "ffmpeg -i " + filename + " -ab 160k -ac 2 -ar 44100 -vn temp.wav"
    os.system(command)


# Criando buffer com frames do video
def VideoBufferCreate():
    WIDTH=400                                           # tamanho optimizado para melhor transmissao
    while(vid.isOpened()):                              # percorre todo video, redimensiona frames e os armazena no buffer
        try:
            _,frame = vid.read()
            frame = imutils.resize(frame, width=WIDTH)
            videoBuffer.put(frame)
        except:
            os._exit(1)
    cv2.destroyAllWindows()
    print('Connection to', cAddress, 'is closed...')
    vid.release()                                       # libera video auxiliar


# Transporte dos frames do video por UDP
def VideoStreaming():
    sleep(1)                                                                                # delay para sincronizacao entre audio e video
    global vidTS
    fps, st, ftc, cnt = (0,0,1,0)                                                           # dados de contagem dos frames
    cv2.namedWindow(('Transmitindo ' + filename + '...'))
    cv2.moveWindow(('Transmitindo ' + filename + '...'), 10, 30) 

    while True: 
        try:                                                                            # enquanto tiver frames, envia para o cliente
            frame = videoBuffer.get()                                                               # pega um frame do video
            encoded,buffer = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])           # formata em jpeg para otimizar envio
            frameData = base64.b64encode(buffer)
            serverSocket.sendto(frameData, cAddress)                                                # manda frame para cliente

            #frame = cv2.putText(frame, 'FPS: '+str(round(fps,1)), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)  # legenda com os frames da reproducao

            # sincroniza velocidade de frames do video com a transmissao
            if cnt == ftc:
                try:
                    fps = (ftc/(time.time()-st))
                    st=time.time()
                    cnt=0
                    if fps>vidFPS:
                        vidTS+=0.001
                    elif fps<vidFPS:
                        vidTS-=0.001
                    else:
                        pass
                except:
                    pass
            cnt+=1
            
            cv2.imshow(('Transmitindo ' + filename + '...'), frame)                                 # mostra frame na tela
            key = cv2.waitKey(int(1000*vidTS)) & 0xFF
            if key == ord('q'):	                                                                    # caso 'q' seja apertado, fecha video
                os._exit(1)	
        
        except:
            break

    cv2.destroyAllWindows()


# Convertendo arquivos MP3 para um temporario WAV
def AudioConverting():
    command = "rm temp.wav"
    os.system(command)
    srcFile = "temp.wav"
    sound = AudioSegment.from_mp3(filename)
    sound.export(srcFile, format="wav")

    return srcFile


# Transporte do audio do video por TCP
def AudioStreaming():
    global audiofile
    audioSocket = socket.socket()
    audioSocket.bind((serverIP, (serverPort-1)))                # cria um socket para transmissao do audio com cliente

    audioSocket.listen(5)
    CHUNK = 1024
    wf = wave.open(audiofile, 'rb')                             # estrutura para reproducao do video

    clientSocket,addr = audioSocket.accept()                    # verifica se a conexao foi estabelecida

    while True:
        if clientSocket:
            while True:
                data = wf.readframes(CHUNK)
                a = pickle.dumps(data)
                audioData = struct.pack("Q", len(a)) + a
                clientSocket.sendall(audioData)                 # envia pacote com audio para o cliente


# Download de arquivos via TCP
def SendToClient():
    stcSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stcSocket.bind((serverIP, serverPort-1))                      # socket para envio dos dados
    stcSocket.listen(1)
    clientSocket,addr = stcSocket.accept()                      # verifica se a conexao foi estabelecida

    with open(filename, 'rb') as filedata:                      # abre arquivo desejado
        print("Enviando",filename,'...')
        for data in filedata.readlines():
            clientSocket.send(data)                             # envia linhas do arquivo para o cliente


# Upload de arquivos via TCP
def RecvFromClient():
    stcSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stcSocket.bind((serverIP, serverPort-1))                      # socket para envio dos dados
    stcSocket.listen(1)
    clientSocket,addr = stcSocket.accept()                      # verifica se a conexao foi estabelecida

    with open(filename, 'wb') as filedata:
        print("Recebendo",filename,'...')
        while 1:
            data = clientSocket.recv(1000000)                   # recebe pacotes contendo dados do arquivo
            if not data:
                break
            filedata.write(data)                                # armazena dados recebidos em um arquivo




# Main
#variaveis de buffer
global audiofile
BUFFSIZE = 65536

# dados de conexao
serverIP = sys.argv[1]
serverPort = 8081

while True:
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,BUFFSIZE)
    hostname = socket.gethostname()

    # realiza conexao entre cliente e o servidor, esperando endereco do arquivo
    sAddress = (serverIP, serverPort)
    serverSocket.bind(sAddress)                                         # abre conexao com o cliente
    print('The server started at', sAddress)

    msg, cAddress = serverSocket.recvfrom(BUFFSIZE)                     # recebe o endereco do arquivo desejado do cliente
    print(msg)
    filen = msg.decode("utf-8")                                         # decodifica endereco
    print('Conexao com', cAddress, 'estabelecida...\n')
    filen = filen.split('//')
    print(filen[0])
    filename = filen[1]

    if(filen[0] == 'VIEW'):                                                 # caso de streaming de arquivo

        if(os.path.isfile(filename)):
            if('.mp4' in filename):                                         # caso o arquivo seja um video
                videoBuffer = queue.Queue(maxsize=10)

                audiofile = "temp.wav"
                print(filename)

                AudioBufferCreate()                                         # converte faixa de audio em um temporario WAV

                # extrai os dados de fps e velocidade e tempo do video 
                vid = cv2.VideoCapture(filename)
                vidFPS = vid.get(cv2.CAP_PROP_FPS)
                global vidTS
                vidTS = (0.5/vidFPS)
                vidTNF = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = float(vidTNF) / float(vidFPS)
                d = vid.get(cv2.CAP_PROP_POS_MSEC)
                print(duration, d)
                
                # paraleliza UDP com TCP (frames com audio)
                with ThreadPoolExecutor(max_workers=3) as executor:
                    executor.submit(AudioStreaming)
                    executor.submit(VideoBufferCreate)
                    executor.submit(VideoStreaming)

            elif('.wav' in filename):                                       # caso o arquivo seja um audio
                audiofile = filename
                print("Reproduzindo",sys.argv[3],'...')
                AudioStreaming()                                            # envia o arquivo via TCP

            elif('.mp3' in filename):                                       # caso o arquivo seja um audio
                audiofile = AudioConverting()
                print("Reproduzindo",sys.argv[3],'...')
                AudioStreaming()                                            # envia o arquivo via TCP

            else:                                                           # caso seja outro tipo de arquivo, da erro
                print('Formato invalido!')
                os._exit(1)

        else:                                                               # caso o arquivo nao esteja no servidor, da erro
            print("Arquivo " + filename + " n??o encontrado!")
            os._exit(1)


    elif(filen[0] == 'GET'):                                                # caso de download de arquivo
        SendToClient()                                                  # tenta enviar arquivo via TCP para o cliente
        print(filename, 'enviado com sucesso!\n')


    elif(filen[0] == 'POST'):                                                # caso de upload de arquivo
        RecvFromClient()
        print(filename, 'recebido com sucesso!\n')

    elif(filen[0] == 'SHUTDOWN'):                                                # caso de upload de arquivo
        print('Server encerrado por cliente!\n')
        os._exit(1)

    else:
	    print('Operacao invalida! Use outra\n')
	    os._exit(1)
