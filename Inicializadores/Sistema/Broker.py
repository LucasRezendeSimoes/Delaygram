import zmq
import time
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
    socketh = context.socket(zmq.ROUTER)
    socketh.bind("tcp://localhost:5559")
    poller.register(socketh, zmq.POLLIN)

    while True:
        if socketh.poll(1000):  # Espera 1 segundo
            batida = socketh.recv_multipart()
            id_servidor = batida[0]
            print(f"[💓HEARTBEAT RECEBIDO] De {id_servidor}")
            servidores[id_servidor] = time.time()  # salva timestamp atual

        # Verifica quais servidores passaram do tempo de timeout
        agora = time.time()
        removidos = []
        for id_servidor, ultimo_heartbeat in servidores.items():
            if agora - ultimo_heartbeat > 10:  # 10 segundos sem heartbeat
                print(f"[SERVIDOR REMOVIDO] {id_servidor}")
                removidos.append(id_servidor)

        for r in removidos:
            del servidores[r]

        print("Servidores ativos:", list(servidores.keys()))
        time.sleep(1)

        
        

TProxy = threading.Thread(target=proxy, daemon=True)
TProxy.start()
THeartbeat = threading.Thread(target=heartbeat, daemon=True)
THeartbeat.start()

print("\033[31mBroker - 0")

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