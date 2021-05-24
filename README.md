# Redes-T1
Uma aplicação de streaming de video utilizando UDP e TCP

------

# Bibliotecas Necessarias
- opencv-python
- pickle5
- wave
- pydub
- PyAudio
    - no site do PyPi (para python 3.6 ou anterior)
    - arquivo na pasta para versao windows (pip install DPyAudio-0.2.11-cp39-cp39-win_amd64.whl)

------

# Executar
###Server Side: python Server.py IPADDRESS
###Client Side: python Client.py IPADDRESS FUNC FILENAME

- IPADDRESS = endereço do IP. Exemplo 127.0.0.1
- FILENAME = use nomes de arquivos sem espaço, usando _ no lugar
- FUNC = funcoes de interação com o servidor
    - -v = reproduzir arquivo de mídia
    - -d = baixar arquivo do servidor
    - -u = enviar arquivo para o servidor
    - -end = fechar servidor

- Formatos Validos: MP3, MP4, WAV

- Arquivos de Teste:
    - tres_espias_demais.mp4
    - Take-On-Me.mp3
    - rick_n_roll.mp4
    - Hotline_Original.wav

# Observações
- Possíveis atrasos no áudio podem ocorrer para vídeos longos