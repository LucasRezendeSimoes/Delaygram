import zmq
import threading
from time import sleep
import time
from datetime import datetime

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect("tcp://localhost:5556")  # conecta no broker local

ctx = zmq.Context.instance()
pub = ctx.socket(zmq.PUB)
pub.connect("tcp://localhost:5558")

# Socket para broker berkeley
sync_socket = context.socket(zmq.DEALER)
sync_socket.setsockopt(zmq.IDENTITY, b'server1')  # Altere conforme o ID do servidor
sync_socket.connect("tcp://localhost:5560")

gerente_atual = b'server1'
#-----------------------------------------------------------------------------------
print("\033[34mServer - 1")

# LEMBRA DE TIRAR O IDENTIFY DESSA BAGAÇA

def heartbeat():
    global context
    socketh = context.socket(zmq.DEALER)
    socketh.setsockopt(zmq.IDENTITY, b'server1')  # Define identidade clara
    socketh.connect("tcp://localhost:5559")

    while True:
        socketh.send_multipart([b'server1', b'HEARTBEAT'])
        print("[HEARTBEAT ENVIADO] Para broker: server1 - HEARTBEAT")
        sleep(5)

thread = threading.Thread(target=heartbeat, daemon=True)
thread.start()

def horario_estah_dentro_da_margem(horario_cliente):
    horario_atual = time.time()
    diferenca = abs(horario_cliente - horario_atual)
    return diferenca <= 60  # margem de erro de 60 segundos

def consultar_gerente(horario_cliente):
    sync_socket.send(str(horario_cliente).encode())
    
    if sync_socket.poll(3000):  # 3 segundos para resposta
        resposta = sync_socket.recv()
        return resposta.decode()
    else:
        print("[❌ ERRO] Gerente não respondeu!")
        return "FALSO"

while True:
    message = socket.recv_string()

    if message[0] == '0':
        # Publicação comum
        dados = message.split(':', 2)
        id_remetente = dados[1]
        conteudo = dados[2]

        horario_cliente = time.time()  # Aqui simularíamos com horário embutido na mensagem

        if horario_estah_dentro_da_margem(horario_cliente):
            print("[✅ HORÁRIO OK] Publicando mensagem.")
            pub.send_string(f"{id_remetente}:{conteudo}")
            resposta = "Publicação enviada!"
        else:
            print("[⚠️SINCRONIZAÇÃO] Fora da margem, consultando gerente...")
            resultado = consultar_gerente(horario_cliente)

            if resultado == "OK":
                print("[🟢Gerente aprovou] Publicando com ajuste.")
                pub.send_string(f"{id_remetente}:{conteudo}")
                resposta = "Publicação enviada com horário ajustado!"
            else:
                print("[🔴Gerente rejeitou] Mensagem descartada.")
                resposta = "Publicação rejeitada por horário inválido."

    elif message[0] == '1':
        # Envio de mensagem privada
        dados = message.split(':', 3)
        id_destinatario = dados[2]
        id_remetente = dados[1]
        conteudo = dados[3]
        pub.send_string(f"MSG{id_destinatario}:{id_remetente}:{conteudo}")
        resposta = f"Mensagem enviada para {id_destinatario}"

    elif message[0] == '2':
        # Mudança de subscrição
        dados = message.split(':', 2)
        resposta = f"Subscrição modificada para {dados[2]}"

    else:
        resposta = "Erro: tipo de mensagem desconhecido."

    socket.send_string(resposta)