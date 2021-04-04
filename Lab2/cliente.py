# Lado cliente: Espera o nome do arquivo pelo usuario e o envia ao servidor para leitura e processamento
# Na resposta, verifica se eh uma msg de erro ou um json com as palavras mais comuns do arquivo e printa o resultado
# Continua a espera de nome de arquivo para processamento ate o usuario entrar com a msg para parar.

import socket

HOST = 'localhost' # maquina onde esta o par passivo
PORTA = 5000       # porta que o par passivo esta escutando

# cria socket
sock = socket.socket() # default: socket.AF_INET, socket.SOCK_STREAM 

# conecta-se com o par passivo
sock.connect((HOST, PORTA)) 

print("Para encerrar o programa entre com a mensagem: 'Encarrar conexao'.")
while True:
    inputText = input("Entre com o nome do arquivo para busca: ") #le input do usuario
    #caso o usuario entre com a msg 'Encerrar conexao' quebra o loop de envio e leitura
    if inputText.upper() == 'Encerrar conexao'.upper(): 
        break
    
    # envia uma mensagem para o par conectado
    sock.send(inputText.encode())

    #espera a resposta do par conectado (chamada pode ser BLOQUEANTE)
    msg = sock.recv(1024) # argumento indica a qtde maxima de bytes da mensagem

    msg = str(msg, encoding='utf-8')
    if not msg: 
        print("Mensagem nao recebida do servidor.") 
    elif msg[0:5].upper() == 'Erro:'.upper(): #verifica se reposta do servidor foi de erro
        print(msg)
    else:
        wordDict = eval(msg) #caso resposta nao seja de erro, passa msg para dicionario do python
        print("Palavras mais comuns no arquivo:", inputText)
        for item in wordDict.items(): #imprime cada item dicionario
            print(item)

# encerra a conexao
sock.close() 
