import zmq

ctx = zmq.Context()

# PUB para distribuir publicações
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5558")

print("Servidor 2 iniciado")

while True:
    msg = rep.recv_string()
    
    if msg.startswith("POST"):
        # Exemplo: POST:0001:10:Mensagem
        _, user_id, timestamp, texto = msg.split(":", 3)
        mensagem_publicada = f"{user_id}:POST:{timestamp}:{texto}"
        print(f"[PUB] {mensagem_publicada}")
        pub.send_string(mensagem_publicada)
        rep.send_string("Publicação enviada com sucesso.")
    else:
        rep.send_string("Mensagem não reconhecida.")
