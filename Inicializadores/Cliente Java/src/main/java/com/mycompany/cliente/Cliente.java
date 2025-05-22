package com.mycompany.cliente;
import org.zeromq.ZMQ;
import org.zeromq.ZContext;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;

public class Cliente {
    static class User {
        String id = "0007";
        String name = "Claudia";
        List<String> seguindo = new CopyOnWriteArrayList<>();
        List<String> mailbox = new CopyOnWriteArrayList<>();
    }

    static final User user = new User();
    static final List<String> tags = Arrays.asList("0", "1", "2", "3");

    static ZContext context = new ZContext();
    static ZMQ.Socket socket = context.createSocket(ZMQ.REQ);
    static ZMQ.Socket sub = null;

    static Thread subThread = null;
    static volatile boolean subStop = false;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        socket.connect("tcp://localhost:5555");

        atualizarSubscricoes();

        System.out.println("Cliente - 0");

        while (true) {
            exibirMailbox();

            System.out.println("\nOpcoes:");
            System.out.println("0: Publicacao\n1: Mensagem privada\n2: Subscricao\n3: Atualizar");

            String tag = "";
            while (true) {
                System.out.print("Digite o tipo de mensagem: ");
                tag = sc.nextLine().trim();
                if (!tags.contains(tag)) {
                    System.out.println("TAG INVALIDA!");
                } else {
                    break;
                }
            }

            StringBuilder msg = new StringBuilder();
            if (!tag.equals("3")) {
                msg.append(tag).append(":").append(user.id);

                if (tag.equals("0")) {
                    System.out.print("Digite a mensagem: ");
                    String conteudo = sc.nextLine();
                    msg.append(":").append(conteudo);

                } else if (tag.equals("1")) {
                    System.out.print("Enviar para: ");
                    String destinatario = sc.nextLine();
                    System.out.print("Digite a mensagem: ");
                    String conteudo = sc.nextLine();
                    msg.append(":").append(destinatario).append(":").append(conteudo);

                } else if (tag.equals("2")) {
                    System.out.print("Usuario: ");
                    String alvo = sc.nextLine();
                    msg.append(":").append(alvo);

                    if (user.seguindo.contains(alvo)) {
                        user.seguindo.remove(alvo);
                        System.out.println("Voce parou de seguir " + alvo);
                    } else {
                        user.seguindo.add(alvo);
                        System.out.println("Voce comecou a seguir " + alvo);
                    }

                    atualizarSubscricoes();
                }

                msg.append(":").append(System.currentTimeMillis());

                socket.send(msg.toString().getBytes(ZMQ.CHARSET));
                byte[] resposta = socket.recv(0);
                System.out.println("[Servidor]: " + new String(resposta, ZMQ.CHARSET));
            } else {
                System.out.println("Atualizando... (nenhuma acao enviada)");
            }
        }
    }

    static void exibirMailbox() {
        System.out.println("\nCaixa de mensagens:");
        for (String m : user.mailbox) {
            System.out.println(" - " + m);
        }
    }

    static void escutarMensagens() {
        while (!subStop) {
            byte[] msg = sub.recv(ZMQ.DONTWAIT);
            if (msg != null) {
                user.mailbox.add(new String(msg, ZMQ.CHARSET));
            }

            try {
                Thread.sleep(100);  // alivia a CPU
            } catch (InterruptedException ignored) {}
        }
    }

    static void atualizarSubscricoes() {
        // Para a thread antiga
        subStop = true;
        if (subThread != null && subThread.isAlive()) {
            try {
                subThread.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        // Fecha socket antigo
        if (sub != null) {
            sub.close();
        }

        // Recria socket e subscricoes
        sub = context.createSocket(ZMQ.SUB);
        sub.connect("tcp://localhost:5557");

        sub.subscribe(("MSG" + user.id).getBytes(ZMQ.CHARSET));
        for (String seguido : user.seguindo) {
            sub.subscribe(seguido.getBytes(ZMQ.CHARSET));
        }

        System.out.println("[SUBSCRIPCOES ATUALIZADAS] Seguindo: " + user.seguindo);

        subStop = false;
        subThread = new Thread(Cliente::escutarMensagens);
        subThread.setDaemon(true);
        subThread.start();
    }
}
