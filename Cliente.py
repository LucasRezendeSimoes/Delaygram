import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555") # Utilizado para enviar mensagens aos servidores.

sub = context.socket(zmq.SUB)
sub.connect("tcp://localhost:5556") # Utilizado para receber mensagens dos servidores.

user = {
    "id": "0000",
    "time": 0,
    "mailbox": []
}

print("client")

while True:
    msg = input("Digite a mensagem:")
    socket.send_string(f"{user["id"]}:{user["time"]}:{msg}") # envia mensagem (request)
    mensagem = socket.recv_string() # recebe mensagem (reply)
    print(f"{mensagem}")
