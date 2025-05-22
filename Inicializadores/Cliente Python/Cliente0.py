import zmq
import time
import threading

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")  # Envia mensagens ao broker

# Informações do cliente
user = {
    "id": "0000",
    "name": "Geraldo",
    "time": 0,
    "seguindo": [],
    "mailbox": []
}

sub = None  # Socket SUB global para atualizações dinâmicas
sub_thread = None
sub_stop = threading.Event()


def escutar_mensagens():
    """Thread para escutar publicações públicas e mensagens privadas"""
    global sub
    while not sub_stop.is_set():
        try:
            if sub.poll(1000):  # espera até 1s por mensagem
                msg = sub.recv_string()
                user["mailbox"].append(msg)
        except zmq.error.ZMQError:
            break


def atualizar_subscricoes():
    global sub, sub_thread, sub_stop

    # Para a thread antiga com segurança
    if sub_thread and sub_thread.is_alive():
        sub_stop.set()
        sub_thread.join()

    sub_stop.clear()
    if sub:
        try:
            sub.close()
        except:
            pass

    sub = zmq.Context.instance().socket(zmq.SUB)
    sub.connect("tcp://localhost:5557")

    # Subscrição às mensagens privadas
    sub.setsockopt_string(zmq.SUBSCRIBE, f"MSG{user['id']}")

    # Subscrição às mensagens públicas dos usuários seguidos
    for seguido in user["seguindo"]:
        sub.setsockopt_string(zmq.SUBSCRIBE, seguido)

    print(f"[📡 SUBSCRIÇÕES ATUALIZADAS] Seguindo: {user['seguindo']}")

    # Reinicia a thread de escuta
    sub_thread = threading.Thread(target=escutar_mensagens, daemon=True)
    sub_thread.start()


# Inicializa as subscrições
atualizar_subscricoes()

print("\033[32mCliente - 0")
tags = ("0", "1", "2", "3")  # Pub, Dm, Sub, Att

while True:
    print(f"\n📥 Caixa de mensagens:")
    for m in user["mailbox"]:
        print(f" - {m}")
    print("\nOpções:")
    print("0: Publicação\n1: Mensagem privada\n2: Subscrição\n3: Atualizar")

    msg = ""
    while True:
        tag = input("Digite o tipo de mensagem: ")
        if tag not in tags:
            print("TAG INVÁLIDA!")
        else:
            msg += tag
            break

    if int(tag) != 3:
        msg += f":{user['id']}"

        if int(tag) == 0:  # Publicação pública
            conteudo = input("Digite a mensagem: ")
            msg += f":{conteudo}"

        elif int(tag) == 1:  # Mensagem privada
            destinatario = input("Enviar para: ")
            msg += f":{destinatario}"
            conteudo = input("Digite a mensagem: ")
            msg += f":{conteudo}"

        elif int(tag) == 2:  # Subscrição
            alvo = input("Usuário: ")
            msg += f":{alvo}"

            if alvo in user["seguindo"]:
                user["seguindo"].remove(alvo)
                print(f"🚫 Você parou de seguir {alvo}")
            else:
                user["seguindo"].append(alvo)
                print(f"✅ Você começou a seguir {alvo}")

            atualizar_subscricoes()

        timestamp = str(time.time())
        msg += f":{timestamp}"

        socket.send_string(msg)
        resposta = socket.recv_string()
        print(f"[Servidor]: {resposta}")

    else:
        print("🔄 Atualizando... (nenhuma ação enviada)")
