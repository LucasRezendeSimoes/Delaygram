import zmq
import threading
from time import sleep

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect("tcp://localhost:5556")  # conecta no broker local

ctx = zmq.Context.instance()
pub = ctx.socket(zmq.PUB)
pub.connect("tcp://localhost:5558")

print("\033[34mServer - 2")

def heartbeat():
    global context
    socketh = context.socket(zmq.DEALER)
    socketh.setsockopt(zmq.IDENTITY, b'server2')  # Define identidade clara
    socketh.connect("tcp://localhost:5559")

    while True:
        socketh.send_multipart([b'server1', b'HEARTBEAT'])
        print("[HEARTBEAT ENVIADO] Para broker: server1 - HEARTBEAT")
        sleep(5)

thread = threading.Thread(target=heartbeat, daemon=True)
thread.start()

while True:
    message = socket.recv_string()
    if message[0] == '0':
        dados = message.split(':', 2)
        msg = f"{dados[1]}:{dados[2]}"
        resposta = "Publicação enviada!"
        pub.send_string(msg)
    elif message[0] == '1':
        dados = message.split(':', 3)
        msg = f"MSG{dados[2]}:{dados[1]}:{dados[3]}"
        resposta = f"Mensagem enviada para {dados[2]}"
        pub.send_string(msg)
    elif message[0] == '2':
        dados = message.split(':', 2)
        resposta = f"Subscrição modificada para {dados[2]}"
    else:
        resposta = "Erro: tipo de mensagem desconhecido."

    socket.send_string(resposta)