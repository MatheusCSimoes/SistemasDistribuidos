import rpyc
import hashlib

Nnodes = 64

class Node(rpyc.Service):
    def __init__(self, nid):
        self.id = nid
        self.successor = [0,0]
        self.ft = dict()
        self.values = dict()

    def on_connect(self, conx):
        #print("Conexao estabelecida.")
        return

    def on_disconnect(self, conx):
        #print("Conexao encerrada.")
        return

    def get_hash(self, key):
        #https://stackoverflow.com/questions/2706033/split-entire-hash-range-into-n-equal-ranges
        bucketSize = 2**160/Nnodes

        hash = hashlib.sha1(key.encode()).hexdigest()
        keyId = int(int(hash, 16) / bucketSize)

        return keyId

    def exposed_set_ft(self, ft):
        self.ft = ft
        self.successor = ft[0]
        #print('inside node', self.id, '-> ft:', self.ft)
        #print('successor:', self.successor)
        return

    def exposed_get_ft(self):
        print('exposed_get_ft', self.ft)

    def exposed_get_value(self, key):
        return self.values.get(key, 'Chave/Valor não encontrado.')

    def exposed_add_value(self, key, value):
        self.values[key] = value
        return 'valor adicionado no nó' + str(self.id)

    def exposed_search(self, key):
        keyId = self.get_hash(key) #pegar hash da chave
        
        keyNodePair = self.exposed_find_successor(keyId)
        
        if keyNodePair[0] == self.id:
            return self.exposed_get_value(key)
        else:
            next_node_connection = rpyc.connect('', keyNodePair[1])
            value = next_node_connection.root.exposed_get_value(key)
            next_node_connection.close()
            return value

    def exposed_insert_value(self, key, value):
        keyId = self.get_hash(key) #pegar hash da chave

        print('exposed_insert_value', self.id)

        keyNodePair = self.exposed_find_successor(keyId)
        
        print('keyNodeId', keyNodePair)
        
        if keyNodePair[0] == self.id:
            return self.exposed_add_value(key, value)
        else:
            next_node_connection = rpyc.connect('', keyNodePair[1])
            answer = next_node_connection.root.exposed_add_value(key, value)
            next_node_connection.close()
            return answer

    def exposed_find_successor(self, keyId):        
        print('exposed_find_successor', self.id, keyId)
        print('ft', self.ft)

        if self.id < self.successor[0] and self.id < keyId <= self.successor[0]:
            return self.successor
        elif self.id > self.successor[0] and (self.id < keyId or keyId <= self.successor[0]):
            return self.successor
        else:
            nextNode = self.closest_preceding_node(keyId)

            if keyId == self.id:
                return nextNode

            #print('nextNode', nextNode)

            next_node_connection = rpyc.connect('', nextNode[1])
            key_succ = next_node_connection.root.exposed_find_successor(keyId)
            next_node_connection.close()

            return key_succ
    
    def closest_preceding_node(self, keyId):
        for i in sorted(self.ft, reverse=True):
            if self.id < keyId and self.id < self.ft[i][0] < keyId:
                return self.ft[i]
            elif self.id > keyId and (self.id < self.ft[i][0] or self.ft[i][0] < keyId):
                return self.ft[i]

        return [self.id, -1]