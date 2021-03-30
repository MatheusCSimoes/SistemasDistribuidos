# Exemplo basico socket (lado ativo)

import socket

HOST = 'localhost' # maquina onde esta o par passivo
PORTA = 5000        # porta que o par passivo esta escutando

# cria socket
sock = socket.socket() # default: socket.AF_INET, socket.SOCK_STREAM 

# conecta-se com o par passivo
sock.connect((HOST, PORTA)) 

print("Para encerrar o programa entre com a mensagem: 'Encarrar conexao'.")
while True:
    inputText = input("Entre com a mensagem para o servidor de echo: ") #le input do usuario
    #caso o usuario entre com a msg 'Encerrar conexao' quebra o loop de envio e leitura
    if inputText.upper() == 'Encerrar conexao'.upper(): 
        break
    
    # envia uma mensagem para o par conectado
    sock.send(inputText.encode())

    #espera a resposta do par conectado (chamada pode ser BLOQUEANTE)
    msg = sock.recv(1024) # argumento indica a qtde maxima de bytes da mensagem

    # imprime a mensagem recebida
    print('Mensagem recebida do passivo:', str(msg,  encoding='utf-8'))

# encerra a conexao
sock.close() 
