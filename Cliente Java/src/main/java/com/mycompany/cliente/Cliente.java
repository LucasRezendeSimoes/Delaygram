package com.mycompany.cliente;
import org.zeromq.ZMQ;
import org.zeromq.ZContext;

import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;

public class Cliente {
    static class User {
        String id = "0000";
        String name = "Geraldo";
        int time = 0;
        List<String> seguindo = new ArrayList<>();
        List<String> mailbox = new CopyOnWriteArrayList<>();
    }

    public static void main(String[] args) {
        User user = new User();

        try (ZContext context = new ZContext()) {
            ZMQ.Socket socket = context.createSocket(ZMQ.REQ);
            socket.connect("tcp://localhost:5555");

            Thread subThread = new Thread(() -> {
                ZMQ.Socket sub = context.createSocket(ZMQ.SUB);
                sub.connect("tcp://localhost:5557");

                sub.subscribe(("MSG" + user.id).getBytes(ZMQ.CHARSET));
                sub.subscribe("0001".getBytes(ZMQ.CHARSET)); // Teste de subscrição

                while (!Thread.currentThread().isInterrupted()) {
                    String msg = sub.recvStr();
                    user.mailbox.add(msg);
                }

                sub.close();
            });
            subThread.setDaemon(true);
            subThread.start();

            Scanner scanner = new Scanner(System.in);
            String[] tags = {"0", "1", "2", "3"};

            System.out.println("\u001B[32mCliente - 0");

            while (true) {
                System.out.println("Caixa de mensagens:");
                for (String m : user.mailbox) {
                    System.out.println(m);
                }

                System.out.println("0: Publicacao\n1: Mensagem privada\n2: Subscricao\n3: Atualizar");

                String tag = "";
                while (true) {
                    System.out.print("Digite o tipo de mensagem: ");
                    tag = scanner.nextLine();
                    if (!Arrays.asList(tags).contains(tag)) {
                        System.out.println("TAG INVALIDA!");
                    } else {
                        break;
                    }
                }

                StringBuilder msg = new StringBuilder();
                msg.append(tag);

                if (!tag.equals("3")) {
                    msg.append(":").append(user.id);

                    if (tag.equals("0")) { // Publicação
                        System.out.print("Digite a mensagem: ");
                        String conteudo = scanner.nextLine();
                        msg.append(":").append(conteudo);

                    } else if (tag.equals("1")) { // Mensagem privada
                        System.out.print("Enviar para: ");
                        String destinatario = scanner.nextLine();
                        msg.append(":").append(destinatario);

                        System.out.print("Digite a mensagem: ");
                        String conteudo = scanner.nextLine();
                        msg.append(":").append(conteudo);

                    } else if (tag.equals("2")) { // Subscrição
                        System.out.print("Usuario: ");
                        String alvo = scanner.nextLine();
                        msg.append(":").append(alvo);

                        if (user.seguindo.contains(alvo)) {
                            user.seguindo.remove(alvo);
                            System.out.println("Você parou de seguir " + alvo);
                        } else {
                            user.seguindo.add(alvo);
                            System.out.println("Você começou a seguir " + alvo);
                        }
                    }

                    socket.send(msg.toString());
                    String resposta = socket.recvStr();
                    // System.out.println(resposta); // Pode ser usado para debug
                }

                System.out.println("\n");
            }
        }
    }
}

