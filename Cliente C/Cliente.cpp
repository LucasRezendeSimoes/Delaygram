#include <zmq.h>
#include <iostream>
#include <string>
#include <vector>
#include <thread>
#include <sstream>
#include <algorithm>

// Representação do usuário
struct User {
    std::string id = "0000";
    std::string name = "Geraldo";
    int time = 0;
    std::vector<std::string> seguindo;
    std::vector<std::string> mailbox;
};

User user;

// Thread de recebimento de mensagens publicadas
void publicacoes(void* context) {
    void* sub = zmq_socket(context, ZMQ_SUB);
    zmq_connect(sub, "tcp://localhost:5557");

    std::string filtro1 = "MSG" + user.id;
    std::string filtro2 = "0001";

    zmq_setsockopt(sub, ZMQ_SUBSCRIBE, filtro1.c_str(), filtro1.size());
    zmq_setsockopt(sub, ZMQ_SUBSCRIBE, filtro2.c_str(), filtro2.size());

    while (true) {
        char buffer[512] = {0};
        int recv_len = zmq_recv(sub, buffer, sizeof(buffer) - 1, 0);
        if (recv_len > 0) {
            user.mailbox.emplace_back(buffer);
        }
    }

    zmq_close(sub);
}

void print_mailbox() {
    std::cout << "Caixa de mensagens:\n";
    for (const auto& msg : user.mailbox) {
        std::cout << " - " << msg << std::endl;
    }
}

int main() {
    void* context = zmq_ctx_new();
    void* requester = zmq_socket(context, ZMQ_REQ);
    zmq_connect(requester, "tcp://localhost:5555");

    std::thread th(publicacoes, context);
    th.detach(); // não vamos mais nos preocupar com a thread

    std::cout << "\033[32mCliente - 0\033[0m" << std::endl;
    const std::vector<std::string> tags = {"0", "1", "2", "3"};

    while (true) {
        std::string msg;
        print_mailbox();

        std::cout << "0: Publicacao\n1: Mensagem privada\n2: Subscricao\n3: Atualizar" << std::endl;

        std::string tag;
        while (true) {
            std::cout << "Digite o tipo de mensagem: ";
            std::getline(std::cin, tag);
            if (std::find(tags.begin(), tags.end(), tag) == tags.end()) {
                std::cout << "TAG INVALIDA!" << std::endl;
            } else {
                msg += tag;
                break;
            }
        }

        if (tag != "3") {
            msg += ":" + user.id;

            if (tag == "0") {
                std::string conteudo;
                std::cout << "Digite a mensagem: ";
                std::getline(std::cin, conteudo);
                msg += ":" + conteudo;
            } else if (tag == "1") {
                std::string destinatario, conteudo;
                std::cout << "Enviar para: ";
                std::getline(std::cin, destinatario);
                std::cout << "Digite a mensagem: ";
                std::getline(std::cin, conteudo);
                msg += ":" + destinatario + ":" + conteudo;
            } else if (tag == "2") {
                std::string alvo;
                std::cout << "Usuario: ";
                std::getline(std::cin, alvo);
                msg += ":" + alvo;

                auto it = std::find(user.seguindo.begin(), user.seguindo.end(), alvo);
                if (it != user.seguindo.end()) {
                    user.seguindo.erase(it);
                    std::cout << "Voce parou de seguir " << alvo << std::endl;
                } else {
                    user.seguindo.push_back(alvo);
                    std::cout << "Voce comecou a seguir " << alvo << std::endl;
                }
            }

            zmq_send(requester, msg.c_str(), msg.size(), 0);

            char resposta[512] = {0};
            zmq_recv(requester, resposta, sizeof(resposta) - 1, 0);
            // Pode imprimir a resposta se desejar
        }

        std::cout << "\n\n";
    }

    zmq_close(requester);
    zmq_ctx_destroy(context);
    return 0;
}
