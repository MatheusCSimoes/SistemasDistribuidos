import threading
import random
import time
import math
import rpyc
from rpyc.utils.server import ThreadedServer
from node import Node

Nactive = 4 #16
Nnodes = 64

nodeServers = dict()
nodePorts = dict() 
nodeConnections = dict()

def get_successor(id, nodeIdslist):
    for i in nodeIdslist:
        if i >= id:
            return i

    return nodeIdslist[0]

def createFT(nodeId, nodeIdslist):
    global nodePorts
    global nodeServers

    ft = dict()

    for i in range(int(math.log(Nactive, 2)) + 1):
        key = (nodeId + pow(2, i)) % Nnodes
        succ = get_successor(key, nodeIdslist)
        ft[i] = [succ, nodePorts[succ]]

    return ft

def main():
    nodeIds = sorted(random.sample(range(Nnodes), Nactive))
    print('Available node ids:', nodeIds)

    for nodeId in nodeIds:
        node_thread = threading.Thread(target=create_node, args=[nodeId])
        node_thread.start()

    #time.sleep(1)
    while len(nodePorts) < len(nodeIds):
        continue

    for nodeId in nodeIds:
        ft = createFT(nodeId, nodeIds)
        print('FT node', nodeId, '->', ft)

        node_connection = rpyc.connect('', nodePorts[nodeId])
        node_connection.root.exposed_set_ft(ft)

        nodeConnections[nodeId] = node_connection
        #node_connection.close()

    try:
        while True:
            operation = input('\n'
                'Qual operação deseja fazer? Entre com o número correspondente\n'
                '(1) - Listar nós disponíveis\n'
                '(2) - Inserir par chave/valor\n'
                '(3) - Buscar valor por chave\n'
                '(4) - Encerrar\n'
                'Entrada: ')

            if operation == '1':
                print('Nós disponíveis:', nodeIds)
            elif operation == '2':
                nodeId = input('Inserir chave/valor a partir de qual nó? ')
                nodeId = int(nodeId)
                if nodeId not in nodeIds:
                    print('Nó não disponível')
                    continue

                key = input('Qual chave? ')
                value = input('Qual valor? ')

                #node_connection = rpyc.connect('', nodePorts[nodeId])
                node_connection = nodeConnections[nodeId]
                answer = node_connection.root.exposed_insert_value(key, value)
                #node_connection.close()
                print(answer)
            elif operation == '3':
                nodeId = input('Inserir valor a partir de qual nó? ')
                nodeId = int(nodeId)
                if nodeId not in nodeIds:
                    print('Nó não disponível')
                    continue

                key = input('Qual chave? ')

                #node_connection = rpyc.connect('', nodePorts[nodeId])
                node_connection = nodeConnections[nodeId]
                answer = node_connection.root.exposed_search(key)
                #node_connection.close()
                print(answer)
            elif operation == '4':
                break
    except Exception as ex:
        print(ex)
        print('Erro na execução de alguma operação.')

    for nodeId in nodeIds:
        nodeConnections[nodeId].close()
        stop_node(nodeId)

def stop_node(nodeId):
    global nodeServers
    global nodePorts

    if nodeId in nodeServers:
        nodeServers[nodeId].close()
        del nodeServers[nodeId]

def create_node(nodeId):
    global nodeServers
    global nodePorts

    node_server = ThreadedServer(Node(nodeId))

    nodeServers[nodeId] = node_server
    nodePorts[nodeId] = node_server.port
    
    print('node', nodeId, 'created with port:', nodePorts[nodeId])
    nodeServers[nodeId].start()
    print('node', nodeId, 'stopped and thread end')

if __name__ == '__main__':
    main()