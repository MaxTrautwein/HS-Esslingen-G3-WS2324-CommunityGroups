package com.dk4max.HS_Esslingen.communitygroups;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.dk4max.HS_Esslingen.communitygroups.socket.SocketManager;

import org.json.JSONArray;
import org.json.JSONObject;

import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.emitter.Emitter;

public class ChatroomActivity extends AppCompatActivity {

    private EditText newChatName;

    SocketManager socket = SocketManager.getInstance();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.chatrooms);

        ImageView addChat = findViewById(R.id.addChat);
        newChatName = findViewById(R.id.Header);

        socket.getSocket().emit("GetChatGroups", "Filler");
        socket.getSocket().on("reply", createList());

        addChat.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                SocketManager.getInstance().setCurrentChat(newChatName.getText().toString());
                SocketManager.getInstance().setCurrentChatID(-1);
                Intent intent = new Intent(ChatroomActivity.this, ChatActivity.class);
                startActivity(intent);
            }
        });
    }

    private Emitter.Listener createList() {
        return new Emitter.Listener() {
            @Override
            public void call(final Object... args) {
                JSONArray allChats = (JSONArray) args[0];
                TextView templateTextView = findViewById(R.id.chats);
                LinearLayout linearLayout = findViewById(R.id.linearLayout);

                for(int i = 0; i<allChats.length(); i++){
                    try {
                        JSONObject userObject = allChats.getJSONObject(i);
                        int userId = userObject.getInt("user_id");
                        String username = userObject.getString("username");

                        TextView chatTextView = new TextView(ChatroomActivity.this);
                        chatTextView.setLayoutParams(templateTextView.getLayoutParams());
                        chatTextView.setText(templateTextView.getText().toString());
                        chatTextView.setId(View.generateViewId());
                        chatTextView.setTextColor(Color.parseColor("#FFFFFF"));
                        chatTextView.setTextSize(20);


                        chatTextView.setOnClickListener(new View.OnClickListener() {
                            @Override
                            public void onClick(View view) {
                                SocketManager.getInstance().setCurrentChat(username);
                                SocketManager.getInstance().setCurrentChatID(userId);
                                Intent intent = new Intent(ChatroomActivity.this, ChatActivity.class);
                                startActivity(intent);
                            }
                        });
                        chatTextView.setText(username);
                        linearLayout.addView(chatTextView);

                    } catch (Exception e){

                    }
                }


            }
        };
    }
}