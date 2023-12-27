package com.dk4max.HS_Esslingen.communitygroups.socket;
import android.util.Log;
import android.widget.Toast;

import com.dk4max.HS_Esslingen.communitygroups.Auth.AuthStateManager;
import com.dk4max.HS_Esslingen.communitygroups.MainActivity;

import java.util.logging.Logger;

import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.emitter.Emitter;

public class SocketManager {
    private static SocketManager INSTANCE;
    private Socket socket;
    protected AuthState authState = AuthState.Init;


    private SocketManager() {
    }
    public static SocketManager getInstance(){
        if(INSTANCE == null){
            INSTANCE = new SocketManager();
        }
        return INSTANCE;
    }


    public Socket getSocket() {
        if (socket == null) {
            try {
                socket = IO.socket("http://85.215.34.151:5000");
            } catch (Exception e) {
                e.printStackTrace();
            }
        }


        return socket;
    }



    enum AuthState {
        Init,
        Pass,
        Fail
    }


    public void OpenConnection(){
        String Token = AuthStateManager.getInstance(null).getAccessToken();
        Log.d("token",Token);
        OpenConnection(Token);
    }
    public void OpenConnection(String token){
        getSocket();
        socket.connect();
        socket.on("status", authenticationResponse);
        sendAuthentication(token);
    }

    private void sendAuthentication(String token){
        try{
            socket.emit("Auth", token);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }






    private Emitter.Listener authenticationResponse = new Emitter.Listener() {
        @Override
        public void call(final Object... args) {
            String serverResponse = (String) args[0];
            if ("Auth Success".equals(serverResponse)) {
                SocketManager.getInstance().authState = AuthState.Pass;
                Log.d("Auth","Pass");
            } else if ("Token Error".equals(serverResponse)) {
                SocketManager.getInstance().authState = AuthState.Fail;
                Log.d("Auth","Fail");
            }
        }
    };



}