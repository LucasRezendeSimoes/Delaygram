import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socketh = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5556") # conecta no broker local

ctx = zmq.Context.instance()
pub = ctx.socket(zmq.PUB)
pub.connect("tcp://localhost:5558")

print("\033[34mServer - 1")

while True:
    message = socket.recv_string()
    if message[0] == '0':
        dados = message.split(':',2)
        msg = f"{dados[1]}:{dados[2]}"
        resposta = "Publicação enviada!"
        pub.send_string(msg)
    elif message[0] == '1':
        dados = message.split(':',3)
        msg = f"MSG{dados[2]}:{dados[1]}:{dados[3]}"
        resposta = f"Mensagem enviada para {dados[2]}"
        pub.send_string(msg)
    elif message[0] == '2':
        dados = message.split(':',2)
        resposta = f"Subscrição modificada para {dados[2]}"
    else:
        resposta = "Erro: tipo de mensagem desconhecido."

    socket.send_string(resposta)
    


"""
Padrão de respostas (pub-sub):

publicador:conteúdo -> 0000:exemplo
destinatário"MSG":remetente:conteúdo -> 0000MSG:0001:exemplo
"""

"""
    if message[0] == '0':
        dados = message.split(':',2)
        msg = f"{dados[1]}:{dados[2]}"
    elif message[0] == '1':
        dados = message.split(':',3)
        msg = f"{dados[2]}MSG:{dados[1]}:{dados[3]}"
    else:
        dados = message.split(':',2)
    
    pub.send_string(msg)
"""