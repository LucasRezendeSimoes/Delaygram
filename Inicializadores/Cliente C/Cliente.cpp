#include <iostream>
#include <zmq.h>
#include <string>
#include <vector>
#include <thread>
#include <algorithm>
#include <atomic>
#include <chrono>
#include <sstream>

using namespace std;

struct User {
    string id = "0006";
    string name = "Alex";
    vector<string> seguindo;
    vector<string> mailbox;
};

User user;
atomic<bool> sub_stop(false);
thread sub_thread;
void* sub_socket = nullptr;

// Gera timestamp
string get_timestamp() {
    auto now = chrono::system_clock::now();
    auto secs = chrono::system_clock::to_time_t(now);
    auto ms = chrono::duration_cast<chrono::milliseconds>(now.time_since_epoch()) % 1000;

    stringstream ss;
    ss << secs << "." << ms.count();
    return ss.str();
}

// Escuta publicacoes publicas e privadas
void escutar_mensagens(void* context) {
    sub_socket = zmq_socket(context, ZMQ_SUB);
    zmq_connect(sub_socket, "tcp://localhost:5557");

    string priv = "MSG" + user.id;
    zmq_setsockopt(sub_socket, ZMQ_SUBSCRIBE, priv.c_str(), priv.size());

    for (const auto& seguido : user.seguindo) {
        zmq_setsockopt(sub_socket, ZMQ_SUBSCRIBE, seguido.c_str(), seguido.size());
    }

    cout << "[SUBSCRIPCOES ATUALIZADAS] Seguindo: ";
    for (const auto& s : user.seguindo) cout << s << " ";
    cout << endl;

    zmq_pollitem_t items[] = {
        { sub_socket, 0, ZMQ_POLLIN, 0 }
    };

    while (!sub_stop.load()) {
        zmq_poll(items, 1, 1000);  // Espera ate 1s por mensagem

        if (items[0].revents & ZMQ_POLLIN) {
            char msg[512] = {0};
            zmq_recv(sub_socket, msg, sizeof(msg) - 1, 0);
            user.mailbox.emplace_back(msg);
        }
    }

    zmq_close(sub_socket);
    sub_socket = nullptr;
}

// Reinicia a thread de escuta
void atualizar_subscricoes(void* context) {
    if (sub_thread.joinable()) {
        sub_stop.store(true);
        sub_thread.join();
    }

    sub_stop.store(false);
    sub_thread = thread(escutar_mensagens, context);
}

// Exibe a caixa de entrada
void print_mailbox() {
    cout << "\nCaixa de mensagens:\n";
    for (const auto& msg : user.mailbox) {
        cout << " - " << msg << endl;
    }
}

int main() {
    void* context = zmq_ctx_new();
    void* requester = zmq_socket(context, ZMQ_REQ);
    zmq_connect(requester, "tcp://localhost:5555");

    atualizar_subscricoes(context);

    cout << "Cliente - 6" << endl;
    const vector<string> tags = {"0", "1", "2", "3"};

    while (true) {
        string msg;
        print_mailbox();

        cout << "\nOpcoes:\n0: Publicacao\n1: Mensagem privada\n2: Subscricao\n3: Atualizar" << endl;

        string tag;
        while (true) {
            cout << "Digite o tipo de mensagem: ";
            getline(cin, tag);
            if (find(tags.begin(), tags.end(), tag) == tags.end()) {
                cout << "TAG INVALIDA!" << endl;
            } else {
                msg += tag;
                break;
            }
        }

        if (tag != "3") {
            msg += ":" + user.id;

            if (tag == "0") {  // Publicacao
                string conteudo;
                cout << "Digite a mensagem: ";
                getline(cin, conteudo);
                msg += ":" + conteudo;

            } else if (tag == "1") {  // Mensagem privada
                string destinatario, conteudo;
                cout << "Enviar para: ";
                getline(cin, destinatario);
                cout << "Digite a mensagem: ";
                getline(cin, conteudo);
                msg += ":" + destinatario + ":" + conteudo;

            } else if (tag == "2") {  // Subscricao
                string alvo;
                cout << "Usuario: ";
                getline(cin, alvo);
                msg += ":" + alvo;

                auto it = find(user.seguindo.begin(), user.seguindo.end(), alvo);
                if (it != user.seguindo.end()) {
                    user.seguindo.erase(it);
                    cout << "Voce parou de seguir " << alvo << endl;
                } else {
                    user.seguindo.push_back(alvo);
                    cout << "Voce comecou a seguir " << alvo << endl;
                }

                atualizar_subscricoes(context);
            }

            msg += ":" + get_timestamp();

            zmq_send(requester, msg.c_str(), msg.size(), 0);
            char resposta[512] = {0};
            zmq_recv(requester, resposta, sizeof(resposta) - 1, 0);
            cout << "[Servidor]: " << resposta << endl;

        } else {
            cout << "Atualizando... (nenhuma acao enviada)" << endl;
        }

        cout << "\n";
    }

    sub_stop.store(true);
    if (sub_thread.joinable()) sub_thread.join();

    zmq_close(requester);
    zmq_ctx_destroy(context);
    return 0;
}
