import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REP)
socketh = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5556") # conecta no broker local

print("server")

while True:
    message = socket.recv_string()
    socket.send_string("fernando guei")
    print(f"{message}")
