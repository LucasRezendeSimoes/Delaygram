import zmq
import time
import threading

context = zmq.Context()

# Socket para receber heartbeats
heartbeat_socket = context.socket(zmq.ROUTER)
heartbeat_socket.bind("tcp://*:5569")

# Socket de sincronização de horário
sync_socket = context.socket(zmq.ROUTER)
sync_socket.bind("tcp://*:5560")

print("\033[35mBroker Berkeley - Sincronização de horário")

ultima_batida = {}
tempo_timeout = 10  # segundos sem heartbeat para considerar servidor como morto
gerente_atual = None

def monitorar_heartbeat():
    global gerente_atual
    while True:
        try:
            ident, _, msg = heartbeat_socket.recv_multipart(flags=zmq.NOBLOCK)
            print(f"[♥️ HEARTBEAT RECEBIDO] de {ident.decode()}")
            ultima_batida[ident] = time.time()

            if gerente_atual is None:
                gerente_atual = ident
                print(f"[👑 NOVO GERENTE] {gerente_atual.decode()}")
                avisar_novo_gerente(gerente_atual)

        except zmq.Again:
            pass

        if gerente_atual:
            tempo_desde_ultimo = time.time() - ultima_batida.get(gerente_atual, 0)
            if tempo_desde_ultimo > tempo_timeout:
                print(f"[❌ GERENTE CAIU] {gerente_atual.decode()} inativo há {tempo_desde_ultimo:.1f}s")
                gerente_atual = eleger_novo_gerente()

        time.sleep(1)

def eleger_novo_gerente():
    candidatos = [k for k, t in ultima_batida.items() if time.time() - t <= tempo_timeout]
    if not candidatos:
        print("[⚠️ SEM SERVIDORES VIVOS]")
        return None
    novo = sorted(candidatos)[0]
    print(f"[👑 NOVO GERENTE ELEITO] {novo.decode()}")
    avisar_novo_gerente(novo)
    return novo

def avisar_novo_gerente(identidade):
    for servidor in ultima_batida:
        try:
            sync_socket.send_multipart([servidor, b"NOVO_GERENTE", identidade])
        except Exception as e:
            print(f"[Erro ao avisar {servidor.decode()}]: {e}")

# Inicia a thread de heartbeat
threading.Thread(target=monitorar_heartbeat, daemon=True).start()

# Loop principal de sincronização de horário
while True:
    partes = sync_socket.recv_multipart()
    print(f"[RECEBIDO] {len(partes)} partes: {[p for p in partes]}")

    if len(partes) == 3:
        id_servidor, empty, mensagem = partes
    elif len(partes) == 2:
        id_servidor, mensagem = partes
        empty = b''
    else:
        print("⚠️ Erro: número inesperado de partes na mensagem!")
        continue

    if mensagem == b"NOVO_GERENTE":
        continue  # ignora comandos internos

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