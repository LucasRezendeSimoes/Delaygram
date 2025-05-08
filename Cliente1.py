import zmq
import threading

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555") # Utilizado para enviar mensagens aos servidores.

# Informações do cliente
user = {
    "id": "0001",
    "name": "Ronaldo",
    "time": 0,
    "seguindo":[],
    "mailbox": []
}

"""
PUBLICAÇÃO:
0:id:conteudo --split-> [remetente, tag, conteudo]

MENSAGEM PRIVADA:
1:id:destinatario:conteudo --split-> [remetente, tag, destinatario, conteudo]

SUBSCRIÇÃO:
2:id:quem (Inscrito se desinscreve e vice versa)

ERRO:
Oi glr = ERRO (Msg sem tag)
"""

def publicacoes():
    global context, user
    sub = context.socket(zmq.SUB)
    sub.connect("tcp://localhost:5557")
    sub.setsockopt_string(zmq.SUBSCRIBE, "MSG%s"%user['id']) # Contato do cliente

    while True:
        msg = sub.recv_string()
        user['mailbox'].append(msg)


thread = threading.Thread(target=publicacoes, daemon=True)
thread.start()

print("\033[32mCliente - 1")
tags = ("0", "1", "2", "3") # Pub, Dm, Sub

while True:
    msg = ""

    print(f"Caixa de mensagens:\n{user['mailbox']}")
    print("""0: Publicação\n1: Mensagem privada\n2: Subscrição\n3: Atualizar""")

    # Usuário adiciona Tag
    while True:
        tag = input("Digite o tipo de mensagem: ")
        if tag not in tags:
            print("TAG INVÁLIDA!")
        else:
            msg += tag
            break
    
    if int(tag) != 3:
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

        elif int(tag) == 2:  # Subscrição
            alvo = input("Usuário: ")
            msg += f":{alvo}"

            if alvo in user["seguindo"]:
                user["seguindo"].remove(alvo)
                print(f"Você parou de seguir {alvo}")
            else:
                user["seguindo"].append(alvo)
                print(f"Você começou a seguir {alvo}")


        #print(msg)
        socket.send_string(msg) # envia mensagem (request)
        mensagem = socket.recv_string() # recebe mensagem (reply)
        #print(f"{mensagem}  {user['mailbox']}")
    print("\n\n")