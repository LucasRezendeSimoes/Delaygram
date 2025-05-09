import zmq
import threading

context = zmq.Context()
poller = zmq.Poller()

# Comunicação Request-Reply
client_socket = context.socket(zmq.ROUTER)
client_socket.bind("tcp://localhost:5555")
poller.register(client_socket, zmq.POLLIN)
client_count = 0

server_socket = context.socket(zmq.DEALER)
server_socket.bind("tcp://localhost:5556")
poller.register(server_socket, zmq.POLLIN)
server_count = 0

servidores = {}

# Thread para Comunicação Publisher-Subscriber
def proxy():
    global context
    pub = context.socket(zmq.XPUB)
    pub.bind("tcp://localhost:5557")

    sub = context.socket(zmq.XSUB)
    sub.bind("tcp://localhost:5558")
    zmq.proxy(pub, sub)

# Thread para tratar o heartbeat
def heartbeat():
    global context, servidores
    socketh = context.socket(zmq.Router)
    socketh.bind("tcp://localhost:5559") # conecta no Servidor
    poller.register(socketh, zmq.POLLIN)

    while(True):
        if socketh.poll(1000): # Verifica por um segundo se há heartbeats, resetando o contador do servidor caso haja
            batida = socketh.recv_multipart()
            servidores[batida[0]] = 5
        
        for i in servidores.keys(): # Desconta do contador de cada servidor e retira o servidor da lista de servidores caso o contador chegue em 0
            if(servidores[i] <= 0):
                del servidores[i]
            else:
                servidores[i] -= 1
        
        

TProxy = threading.Thread(target=proxy, daemon=True)
THeartbeat = threading.Thread(target=heartbeat, daemon=True)
TProxy.start()
THeartbeat.start()

print("\033[31mBroker")

while True:
    socks = dict(poller.poll())

    if socks.get(client_socket) == zmq.POLLIN:
        client_count += 1
        message = client_socket.recv()
        more = client_socket.getsockopt(zmq.RCVMORE)
        if more:
            server_socket.send(message, zmq.SNDMORE)
        else:
            server_socket.send(message)
        print(f"Client messages: {client_count}")

    if socks.get(server_socket) == zmq.POLLIN:
        server_count += 1
        message = server_socket.recv()
        more = server_socket.getsockopt(zmq.RCVMORE)
        if more:
            client_socket.send(message, zmq.SNDMORE)
        else:
            client_socket.send(message)
        print(f"Server messages: {server_count}")

pub.close()
sub.close()
context.close()