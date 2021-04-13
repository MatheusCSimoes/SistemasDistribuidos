import socket
import select
import sys
import threading

HOST = ''    # '' possibilita acessar qualquer endereco alcancavel da maquina local
PORTA = 5000  # porta onde chegarao as mensagens para essa aplicacao

inputList = [sys.stdin] # lista de entradas para o select
connections = {} # dicionario com conexoes ativas
lock = threading.Lock() # lock para acesso do dicionario 'conexoes'

commandList = '''Lista de comandos:
- "Conexoes": imprime a lista de conexoes ativas com o servidor.
- "Encerrar": solicita o encerramento do servidor e apenas é efetivamente desligado caso não haja conexões ativas.
- "Aguardar e encerrar": fica em espera até todos as conexões sejam fechadas e então encerra o servidor.
- "Help": imprime a lista de comandos.\n'''

def openFile(filename): # "camada de acesso aos dados"
	text = ""
	try:
		f = open(str(filename), "r") #abre o arquivo
		text = f.read() #le texto do arquivo
	except:
		#caso nao seja possivel abrir o arquivo, envia mensagem de erro
		raise Exception(str("Erro: nao foi possivel abrir o arquivo. Tente novamente, lembre-se de inserir o sufixo no nome do arquivo."))

	f.close() #fecha arquivo
	return text #retona texto do arquivo para pocessamento

def getCommonWords(filename): # "camada de processamento"
	text = ""
	try:
		text = openFile(filename) #pega texto do arquivo chamando a "camada de acesso aos dados"
	except Exception as ex:
		return str(ex) #no caso de erro, retorna a mensagem de erro

	text = text.lower() #passa todas as palavras para letra minuscula

	stopwords = ['a', 'o', 'e', 'é', 'de', 'do', 'no', 'são'] #lista de palavras nao importantes
	separators = [' ',',','.','!','?'] #lista de separadores
	for sep in separators:
		text = text.replace(sep, ' ') #substitui os separadores por espaco para realizar o split do texto
	allWords = list(text.split()) #realiza o split para gerar a lista de palavras do texto

	allWords = [word for word in allWords if not word in stopwords] #removendo palavras nao importantes
	words = set(allWords) #lista sem repeticao de palavras
	wordsCount = dict() #dicionario para relacionar palavras a sua contagem de ocorrencia
	for word in words: 
		#para cada palavra diferente no texto: coloca no dicionario o par palavra (key) e contagem (valor)
		wordsCount[word] = allWords.count(word)

	#ordena o dicionario de acordo com os valores da contagem e pega apenas os 10 primeiros
	wordsCount = dict(sorted(wordsCount.items(), key=lambda item: item[1], reverse=True)[:10])
	return str(wordsCount)

def startMainSock():
	# cria um socket para comunicacao
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# vincula a interface e porta para comunicacao
	sock.bind((HOST, PORTA))

	# define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
	sock.listen(5) 

	# configura o socket para o modo nao-bloqueante
	sock.setblocking(False)

	# inclui o socket principal na lista de entradas de interesse
	inputList.append(sock)

	return sock

def acceptConnection(sock):
	# aceita conexao da fila
	newSock, address = sock.accept() # retorna um novo socket e o endereco do par conectado
	print ('Conectado com: ', address)
	
	# registra a nova conexao
	lock.acquire()
	connections[newSock] = address 
	lock.release()

	return newSock, address

def getRequest(sock, address):
	while True:
		msg = sock.recv(1024) # argumento indica a qtde maxima de dados
		if not msg:
			print('Conexao encerrada com:', str(address))

			lock.acquire()
			del connections[sock] #retira o cliente da lista de conexoes ativas
			lock.release()

			sock.close() # encerra a conexao com o cliente
			return 

		filename = str(msg, encoding='utf-8') #pega nome do arquivo da mensagem que veio do cliente
		sock.send(getCommonWords(filename).encode()) #envia resposta do processamento ao cliente 

def main():
	threads = [] #lista de threads criadas para atender as conexoes
	sock = startMainSock()
	print(commandList)
	print('Aguardando conexao')
	while True:
		#espera por qualquer entrada de interesse
		read, write, ex = select.select(inputList, [], [])
		#tratar todas as entradas prontas
		for ready in read:
			if ready == sock:  #pedido novo de conexao
				newSock, address = acceptConnection(sock)
				#cria nova thread para atender o cliente
				thread = threading.Thread(target=getRequest, args=(newSock,address))
				thread.start()
				threads.append(thread) #adiciona thread na lista
			elif ready == sys.stdin: #entrada padrao
				cmd = input()
				if cmd.upper() == 'Encerrar'.upper(): #solicitacao de finalizacao do servidor
					if not connections: #somente termina quando nao houver clientes ativos
						sock.close() #encerra socket principal
						sys.exit() #encerra o servidor
					else: print('Nao podemos encerrar pois ha conexao ativas')
				elif cmd.upper() == 'Aguardar e encerrar'.upper():
					print('Aguardando todas as threads serem terminadas')
					for t in threads: #aguarda todas as threads terminarem
						t.join()
					sock.close() #encerra socket principal
					sys.exit() #encerra o servidor
				elif cmd.upper() == 'Conexoes'.upper(): #outro exemplo de comando para o servidor
					print(str(connections.values()))
				elif cmd.upper() == 'Help'.upper(): #outro exemplo de comando para o servidor
					print(commandList)

main()
