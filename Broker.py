import zmq
import threading

context = zmq.Context()
poller = zmq.Poller()

# Comunicação Request-Reply
client_socket = context.socket(zmq.ROUTER)
client_socket.bind("tcp://*:5555")
poller.register(client_socket, zmq.POLLIN)
client_count = 0

server_socket = context.socket(zmq.DEALER)
server_socket.bind("tcp://*:5556")
poller.register(server_socket, zmq.POLLIN)
server_count = 0

# Thread para Comunicação Publisher-Subscriber
def proxy():
    global context
    pub = context.socket(zmq.XPUB)
    pub.bind("tcp://*:5557")

    sub = context.socket(zmq.XSUB)
    sub.bind("tcp://*:5558")
    zmq.proxy(pub, sub)

thread = threading.Thread(target=proxy, daemon=True)
thread.start()

print("Broker")

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