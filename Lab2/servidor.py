# Lado servidor: Recebe o nome do arquvio pelo cliente e chama a camada de processamento, a camada de 
# processamento chama a camada de acesso aos dados. Caso nao seja possivel abrir o arquivo, eh enviado uma 
# mensagem de erro, caso contrario o texto do arquivo eh enviado como resposta para a camada de processamento.
# Na camada de processamento eh feita a contagem de ocorrencia das palavras no texto e retorna para o lado do 
# cliente um dicionario com as 10 palavra mais comuns e suas respectivas contagens.

import socket

HOST = ''    # '' possibilita acessar qualquer endereco alcancavel da maquina local
PORTA = 5000  # porta onde chegarao as mensagens para essa aplicacao

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

# cria um socket para comunicacao
sock = socket.socket()

# vincula a interface e porta para comunicacao
sock.bind((HOST, PORTA))

# define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
sock.listen(1) 

while True:
	print ('Aguardando conexao')

	# aceita a primeira conexao da fila
	novoSock, endereco = sock.accept() # retorna um novo socket e o endereco do par conectado
	print ('Conectado com: ', endereco)

	while True:
		# depois de conectar-se, espera uma mensagem
		msg = novoSock.recv(1024) # argumento indica a qtde maxima de dados
		if not msg: break 
		else: 
			filename = str(msg, encoding='utf-8') #pega nome do arquivo da mensagem que veio do cliente
			novoSock.send(getCommonWords(filename).encode()) #envia resposta do processamento ao cliente 

	# fecha o socket da conexao
	novoSock.close() 

# fecha o socket principal
sock.close() 
