import zmq
import time

context = zmq.Context()

# Comunicação entre servidores para sincronização de horário
sync_socket = context.socket(zmq.ROUTER)
sync_socket.bind("tcp://*:5560")

print("\033[35mBroker Berkeley - Sincronização de horário")

while True:
    print("Esperando mensagem de sincronização...")
    partes = sync_socket.recv_multipart()
    print(f"[RECEBIDO] {len(partes)} partes: {[p for p in partes]}")

    if len(partes) == 3:
        id_servidor, empty, mensagem = partes
    else:
        print("⚠️ Erro: número inesperado de partes na mensagem!")
        continue

    try:
        horario_cliente = float(mensagem.decode())
    except ValueError:
        print("❌ Erro: mensagem recebida não é um número válido!")
        continue

    horario_gerente = time.time()
    diferenca = abs(horario_cliente - horario_gerente)

    print(f"\n[📡 REQ] De {id_servidor}")
    print(f"  🕐 Horário do servidor  : {horario_cliente}")
    print(f"  🕒 Horário do gerente   : {horario_gerente}")
    print(f"  🔁 Diferença            : {diferenca:.2f} segundos")

    if diferenca <= 60:
        print("  ✅ Resposta: OK")
        sync_socket.send_multipart([id_servidor, b'', b"OK"])
    else:
        print("  ❌ Resposta: FALSO")
        sync_socket.send_multipart([id_servidor, b'', b"FALSO"])