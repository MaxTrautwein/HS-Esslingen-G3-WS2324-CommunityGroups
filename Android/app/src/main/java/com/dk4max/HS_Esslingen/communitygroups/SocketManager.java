package com.dk4max.HS_Esslingen.communitygroups;
import io.socket.client.IO;
import io.socket.client.Socket;

public class SocketManager {

    private static Socket socket;

    private SocketManager() {

    }

    public static Socket getSocket() {
        if (socket == null) {
            try {
                socket = IO.socket("http://85.215.34.151:5000");
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        return socket;
    }
}