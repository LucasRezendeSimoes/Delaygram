import zmq
import threading

context = zmq.Context()

# Socket REQ para enviar mensagens ao servidor
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")  # canal REQ/REP via broker

# SUB para receber publicações
sub = context.socket(zmq.SUB)
sub.connect("tcp://localhost:5557")  # canal XPUB (do proxy)

print("Cliente: 2")

# Informações do usuário
user = {
    "id": "0002",
    "time": 0,
    "seguindo": [],  # IDs de usuários que ele segue
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
