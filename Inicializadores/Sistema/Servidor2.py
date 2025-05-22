import zmq
import threading
from time import sleep
import time
from datetime import datetime
import random

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect("tcp://localhost:5556")  # conecta no broker local

ctx = zmq.Context.instance()
pub = ctx.socket(zmq.PUB)
pub.connect("tcp://localhost:5558")

# Socket para broker berkeley
sync_socket = context.socket(zmq.DEALER)
sync_socket.setsockopt(zmq.IDENTITY, b'server2')  # Altere conforme o ID do servidor
sync_socket.connect("tcp://localhost:5560")

gerente_atual = b'server1'
#-----------------------------------------------------------------------------------
print("\033[34mServer - 2")

# LEMBRA DE TIRAR O IDENTIFY DESSA BAGAÇA

def heartbeat():
    global context
    socketh = context.socket(zmq.DEALER)
    socketh.setsockopt(zmq.IDENTITY, b'server2')  # Define identidade clara
    socketh.connect("tcp://localhost:5559")

    while True:
        socketh.send_multipart([b'server2', b'HEARTBEAT'])
        print("[HEARTBEAT ENVIADO] Para broker: server2 - HEARTBEAT")
        sleep(5)
thread = threading.Thread(target=heartbeat, daemon=True)

def escutar_novo_gerente():
    while True:
        try:
            partes = sync_socket.recv_multipart()
            if len(partes) == 2 and partes[0] == b"NOVO_GERENTE":
                novo_gerente = partes[1]
                global gerente_atual
                gerente_atual = novo_gerente
                print(f"[🔔 NOVO GERENTE ATRIBUÍDO] {gerente_atual.decode()}")
        except Exception as e:
            print(f"[ERRO AO RECEBER NOVO_GERENTE]: {e}")
threading.Thread(target=escutar_novo_gerente, daemon=True).start()

thread.start()

def horario_estah_dentro_da_margem(horario_cliente):
    horario_atual = time.time()
    diferenca = abs(horario_cliente - horario_atual)
    return diferenca <= 60  # margem de erro de 60 segundos

def consultar_gerente(horario_cliente):
    if gerente_atual == b'server2':
        print("[Eu sou o gerente] Verificando horário localmente.")
        # Lógica local do gerente:
        horario_atual = time.time()
        diferenca = abs(horario_cliente - horario_atual)
        if diferenca <= 60:
            return "OK"
        else:
            return "FALSO"

    # Se não for o gerente, envia pro gerente via broker
    sync_socket.send(str(horario_cliente).encode())

    if sync_socket.poll(3000):  # 3 segundos para resposta
        resposta_parts = sync_socket.recv_multipart()
        resposta = resposta_parts[-1]
        return resposta.decode()
    else:
        print("[❌ ERRO] Gerente não respondeu!")
        return "FALSO"

    
def possivelmente_alterar_horario(horario_original):
    if random.random() < 0.3:  # 30% de chance de alterar
        desvio = random.randint(-300, 300)  # até 5 minutos
        horario_alterado = horario_original + desvio
        print(f"[HORÁRIO ALTERADO] Original: {horario_original:.2f} | Alterado: {horario_alterado:.2f}")
        return horario_alterado
    return horario_original


while True:
    message = socket.recv_string()
    print(f"[MENSAGEM RECEBIDA] {message}")  #printa a mensagem recebida

    if message[0] == '0':
        # Publicação comum
        dados = message.split(':', 3)
        id_remetente = dados[1]
        conteudo = dados[2]
        horario_cliente = possivelmente_alterar_horario(float(dados[3]))


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
        dados = message.split(':', 4)
        if len(dados) < 5:
            resposta = "[❌ ERRO] Mensagem privada mal formatada! Esperado: '1:remetente:destinatario:conteudo:horario'"
        else:
            id_destinatario = dados[2]
            id_remetente = dados[1]
            conteudo = dados[3]
            horario_cliente = possivelmente_alterar_horario(float(dados[4]))

            pub.send_string(f"MSG{id_destinatario}:{id_remetente}:{conteudo}")
            resposta = f"Mensagem enviada para {id_destinatario}"


    elif message[0] == '2':
        # Mudança de subscrição
        dados = message.split(':', 3)
        if len(dados) < 4:
            resposta = "[❌ ERRO] Subscrição mal formatada! Esperado: '2:remetente:seguido:horario'"
        else:
            id_seguidor = dados[1]
            id_seguido = dados[2]
            horario_cliente = possivelmente_alterar_horario(float(dados[3]))

            # Envia notificação ao seguido
            pub.send_string(f"MSG{id_seguido}:{id_seguidor}:Subscrição de: {id_seguidor}")
            print(f"[🔔NOTIFICAÇÃO] Enviada para {id_seguido} informando que foi seguido por {id_seguidor}")
            
            resposta = f"Subscrição modificada para {id_seguido}"


    else:
        resposta = "Erro: tipo de mensagem desconhecido."

    socket.send_string(resposta)