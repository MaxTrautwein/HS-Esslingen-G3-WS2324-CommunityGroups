package com.dk4max.HS_Esslingen.communitygroups.socket;
import android.content.Context;
import android.content.Intent;
import android.util.Log;
import android.widget.Toast;

import com.dk4max.HS_Esslingen.communitygroups.Auth.AuthStateManager;
import com.dk4max.HS_Esslingen.communitygroups.ChatroomActivity;
import com.dk4max.HS_Esslingen.communitygroups.MainActivity;

import java.util.logging.Logger;

import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.emitter.Emitter;

public class SocketManager {
    private static SocketManager INSTANCE;
    private Socket socket;
    protected AuthState authState = AuthState.Init;

    private String currentChat = "None";
    private String username = "None";

    private int currentChatID = -1;


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


    public void OpenConnection(Context context) {
        String Token = AuthStateManager.getInstance(null).getAccessToken();
        Log.d("token", Token);
        OpenConnection(context, Token);
    }

    public void OpenConnection(Context context, String token) {
        getSocket();
        socket.connect();
        socket.on("status", authenticationResponse(context));
        sendAuthentication(token);
    }


    private void sendAuthentication(String token){
        try{
            socket.emit("Auth", token);
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    public void setUsername(String name){
        username = name;
    }

    public String getUsername(){
        return username;
    }





    private Emitter.Listener authenticationResponse(final Context context) {
        return new Emitter.Listener() {
            @Override
            public void call(final Object... args) {
                String serverResponse = (String) args[0];

                if ("Auth Success".equals(serverResponse)) {
                    SocketManager.getInstance().authState = AuthState.Pass;
                    Log.d("Auth", "Pass");
                    Intent intent = new Intent(context, ChatroomActivity.class);
                    context.startActivity(intent);
                } else if ("Token Error".equals(serverResponse)) {
                    SocketManager.getInstance().authState = AuthState.Fail;
                    Log.d("Auth", "Fail");
                }
            }
        };
    }

    public void setCurrentChat(String username){
        currentChat = username;
    }

    public String getCurrentChat(){
        return currentChat;
    }

    public void setCurrentChatID(int id){
        currentChatID = id;
    }

    public int getCurrentChatID(){
        return currentChatID;
    }


}