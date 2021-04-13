import socket

HOST = 'localhost' # maquina onde esta o par passivo
PORTA = 5000       # porta que o par passivo esta escutando

# cria socket
sock = socket.socket()

# conecta-se com o par passivo
sock.connect((HOST, PORTA)) 

print("Para encerrar o programa entre com a mensagem: 'Encarrar conexao'.")
while True:
    inputText = input("Entre com o nome do arquivo para busca: ") #le input do usuario
    #caso o usuario entre com a msg 'Encerrar conexao' quebra o loop para encerrar conexao
    if inputText.upper() == 'Encerrar conexao'.upper(): 
        break
    
    # envia uma mensagem para o par conectado
    sock.send(inputText.encode())

    #espera a resposta do par conectado
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
