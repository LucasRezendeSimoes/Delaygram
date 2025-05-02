import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socketh = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5556") # conecta no broker local

ctx = zmq.Context.instance()
pub = ctx.socket(zmq.PUB)
pub.connect("tcp://localhost:5558")

print("server")

while True:
    message = socket.recv_string()
    socket.send_string("fernando guei")

    if message[0] == '0':
        dados = message.split(':',2)
        msg = f"{dados[1]}:{dados[2]}"
    elif message[0] == '1':
        dados = message.split(':',3)
        msg = f"{dados[2]}MSG:{dados[1]}:{dados[3]}"
    else:
        dados = message.split(':',2)
    
    pub.send_string(msg)