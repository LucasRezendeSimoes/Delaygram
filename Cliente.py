import zmq
import threading

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555") # Utilizado para enviar mensagens aos servidores.

# Informações do cliente
user = {
    "id": "0000",
    "name": "Geraldo",
    "time": 0,
    "seguindo":[],
    "mailbox": []
}

"""
PUBLICAÇÂO:
Cliente Geraldo enviando uma publicação para todos que seguem ele
tag: conteúdo
0000: mensagem

MENSAGEM PRIVADA:
Cliente Rogério enviando uma mensagem apenas para o cliente Geraldo
tag(tipo de msg): remetente: conteúdo
0000MSG: 0001:mensagem

------------------------------------------------------------------------
0:id:conteudo --split-> [remetente, tag, conteudo]
1:id:destinatario:conteudo --split-> [remetente, tag, destinatario, conteudo]
2:id:quem (Inscrito se desinscreve e vice versa)

Oi glr = ERRO (Msg sem tag)
"""

def publicacoes():
    global context, user
    sub = context.socket(zmq.SUB)
    sub.connect("tcp://localhost:5557")
    sub.setsockopt_string(zmq.SUBSCRIBE, "%sMSG"%user['id']) # Contato do cliente
    sub.setsockopt_string(zmq.SUBSCRIBE, "0000") # Contato do cliente

    while True:
        msg = sub.recv_string()
        user['mailbox'].append(msg)


thread = threading.Thread(target=publicacoes, daemon=True)
thread.start()

print("Cliente - 1")
tags = ("0", "1", "2")

while True:
    msg = ""

    # Usuário adiciona Tag
    while True:
        print(user['mailbox'])
        tag = input("Digite o tipo de mensagem: ")
        print("""0: Publicação\n1: Mensagem privada\n2: Subscrição""")
        if tag not in tags:
            print("TAG INVÁLIDA!")
        else:
            msg += tag
            break

    # Adiciona ID
    msg += f":{user['id']}"

    # Complementos
    if int(tag) == 0: # Publicação
        conteudo = input("Digite a mensagem: ")
        msg += f":{conteudo}"

    elif int(tag) == 1: # Mensagem privada
        destinatario = input("Enviar para: ")
        msg += f":{destinatario}"
        conteudo = input("Digite a mensagem: ")
        msg += f":{conteudo}"

    elif int(tag) == 2: # Subscrição
        destinatario = input("Enviar para: ")
        msg += f":{destinatario}"


    #print(msg)
    socket.send_string(msg) # envia mensagem (request)
    mensagem = socket.recv_string() # recebe mensagem (reply)
    #print(f"{mensagem}  {user['mailbox']}")