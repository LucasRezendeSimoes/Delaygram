#include <iostream> // Bibioteca base
#include <zmq.h> // Usada para realizar a troca de mensagens com os servidores
#include <string> // Usada para manipular strings
#include <vector> // Usado para armazenar as informações do mailbox e seguindo
#include <thread> // Manipulação de threads para a caixa de entrada
#include <algorithm> // Usado para facilitar a procura na lista de pessoas seguindo

using namespace std;

// Dados do usuário
struct User {
    string id = "0000";
    string name = "Geraldo";
    int time = 0;
    vector<string> seguindo;
    vector<string> mailbox;
};

User user;

// Thread para a caixa de entrada
void publicacoes(void* context) {
    void* sub = zmq_socket(context, ZMQ_SUB);
    zmq_connect(sub, "tcp://localhost:5557");

    string contato = "MSG" + user.id;
    zmq_setsockopt(sub, ZMQ_SUBSCRIBE, contato.c_str(), contato.size());

    string filtro2 = "0001"; // Debug
    zmq_setsockopt(sub, ZMQ_SUBSCRIBE, filtro2.c_str(), filtro2.size());// Debug

    while (true) {
        char msg[512] = {0};
        int recv_len = zmq_recv(sub, msg, sizeof(msg) - 1, 0);
        if (recv_len > 0) {
            user.mailbox.emplace_back(msg);
        }
    }

    zmq_close(sub);
}

// Usado para debug
void print_mailbox() {
    cout << "Caixa de mensagens:\n";
    for (const auto& msg : user.mailbox) {
        cout << " - " << msg << endl;
    }
}

int main() {
    void* context = zmq_ctx_new();
    void* requester = zmq_socket(context, ZMQ_REQ);
    zmq_connect(requester, "tcp://localhost:5555");

    thread th(publicacoes, context);
    th.detach(); // Deixa a thread rodando por conta própria

    cout << "\033[32mCliente - 0\033[0m" << endl;
    const vector<string> tags = {"0", "1", "2", "3"};

    while (true) {
        string msg;
        print_mailbox();

        cout << "0: Publicacao\n1: Mensagem privada\n2: Subscricao\n3: Atualizar" << endl;

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

            if (tag == "0") {
                string conteudo;
                cout << "Digite a mensagem: ";
                getline(cin, conteudo);
                msg += ":" + conteudo;
            } else if (tag == "1") {
                string destinatario, conteudo;
                cout << "Enviar para: ";
                getline(cin, destinatario);
                cout << "Digite a mensagem: ";
                getline(cin, conteudo);
                msg += ":" + destinatario + ":" + conteudo;
            } else if (tag == "2") {
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
            }

            zmq_send(requester, msg.c_str(), msg.size(), 0);

            char resposta[512] = {0};
            zmq_recv(requester, resposta, sizeof(resposta) - 1, 0);
        }

        cout << "\n\n";
    }

    zmq_close(requester);
    zmq_ctx_destroy(context);
    return 0;
}
