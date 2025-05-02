import zmq
import threading

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555") # Utilizado para enviar mensagens aos servidores.

user = {
    "id": "0000",
    "time": 0,
    "mailbox": []
}

def publicacoes():
    global context, user
    sub = context.socket(zmq.SUB)
    sub.connect("tcp://localhost:5557")
    sub.setsockopt_string(zmq.SUBSCRIBE, "%sMSG"%user['id'])

    while True:
        msg = sub.recv_string()
        print(msg)
        user['mailbox'].append(msg)


thread = threading.Thread(target=publicacoes, daemon=True)
thread.start()

print("Cliente - 1")

while True:
    msg = input("Digite a mensagem: ")
    socket.send_string(f"{user["id"]}:{user["time"]}:{msg}") # envia mensagem (request)
    mensagem = socket.recv_string() # recebe mensagem (reply)
    print(f"{mensagem}  {user['mailbox']}")

"""
#-------------------------------------------------------
import zmq
import threading

context = zmq.Context()

# Socket REQ para enviar mensagens ao servidor
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")  # canal REQ/REP via broker

# SUB para receber publicações
sub = context.socket(zmq.SUB)
sub.connect("tcp://localhost:5557")  # canal XPUB (do proxy)

print("Cliente: 1")

# Informações do usuário
user = {
    "id": "0001",
    "time": 0,
    "seguindo": ["0002"],  # IDs de usuários que ele segue
    "mailbox": []
}

# Adiciona subscriptions aos IDs seguidos
for seguido_id in user["seguindo"]:
    sub.setsockopt_string(zmq.SUBSCRIBE, f"{seguido_id}:POST")

def escutar_publicacoes():
    while True:
        msg = sub.recv_string()
        print(f"[PUBLICAÇÃO RECEBIDA] {msg}")

# Iniciar thread para escutar publicações
threading.Thread(target=escutar_publicacoes, daemon=True).start()

print("Cliente iniciado")

# Loop principal de envio de mensagens
while True:
    texto = input("Digite a mensagem a publicar: ")
    user["time"] += 1
    mensagem = f"POST:{user['id']}:{user['time']}:{texto}"
    socket.send_string(mensagem)
    resposta = socket.recv_string()
    print(f"Servidor respondeu: {resposta}")    
    resposta = socket.recv_string()
    print(f"Servidor respondeu: {resposta}")
"""