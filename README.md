# Redes-T1
Uma aplicação de streaming de video utilizando UDP e TCP

#Bibliotecas Necessarias
- opencv-python
- pickle5
- wave
- pydub
- PyAudio
    - no site do PyPi (para python 3.6 ou anterior)
    - arquivo na pasta para versao windows (pip install DPyAudio-0.2.11-cp39-cp39-win_amd64.whl)

#Executar
- Server Side: python Server.py IPADDRESS
- Client Side: python Client.py IPADDRESS FILENAME

IPADDRESS = endereço do IP. Exemplo 127.0.0.1
FILENAME = use nomes de arquivos sem espaço, usando _ no lugar