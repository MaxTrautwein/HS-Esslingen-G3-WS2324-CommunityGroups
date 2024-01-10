package com.dk4max.HS_Esslingen.communitygroups;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.dk4max.HS_Esslingen.communitygroups.socket.SocketManager;

import org.json.JSONArray;
import org.json.JSONObject;

import io.socket.emitter.Emitter;

public class ChatActivity extends AppCompatActivity {
    SocketManager socket = SocketManager.getInstance();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.chat);
        TextView header = findViewById(R.id.Header);
        header.setText(socket.getCurrentChat());

        if(socket.getCurrentChatID() != -1) {
            try {
                JSONObject targetJson = new JSONObject();
                targetJson.put("target", socket.getCurrentChatID());
                socket.getSocket().emit("GetAllChatMsgFor", targetJson);
                socket.getSocket().on("reply", createMessages());
            } catch(Exception e){

            }
        }

        ImageView backButton = findViewById(R.id.imageButton1);
        ImageView sendButton = findViewById(R.id.imageButton2);
        backButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(ChatActivity.this, ChatroomActivity.class);
                startActivity(intent);
            }
        });
        sendButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                try{
                    EditText inputMessage = findViewById(R.id.editTextText);
                    JSONObject message = new JSONObject();
                    message.put("msg", inputMessage.getText());
                    message.put("target", SocketManager.getInstance().getCurrentChat());
                    socket.getSocket().emit("SendMsgToUser", message);

                    LinearLayout linearLayout = findViewById(R.id.linearLayout);
                    TextView templateOwnMessage = findViewById(R.id.OwnMessage);
                    TextView chatTextView = new TextView(ChatActivity.this);
                    chatTextView.setLayoutParams(templateOwnMessage.getLayoutParams());
                    chatTextView.setText(templateOwnMessage.getText().toString());
                    chatTextView.setId(View.generateViewId());
                    chatTextView.setText(inputMessage.getText());
                    chatTextView.setTextColor(Color.parseColor("#FFFFFF"));
                    chatTextView.setTextSize(20);
                    linearLayout.addView(chatTextView);
                    inputMessage.setText("");

                } catch (Exception e){

                }
            }
        });
    }

    private Emitter.Listener createMessages() {
        return new Emitter.Listener() {
            @Override
            public void call(final Object... args) {
                JSONArray allMessages = (JSONArray) args[0];
                TextView templateOwnMessage = findViewById(R.id.OwnMessage);
                TextView templateOthersMessage = findViewById(R.id.OthersMessage);
                LinearLayout linearLayout = findViewById(R.id.linearLayout);

                for(int i = 0; i<allMessages.length(); i++){
                    try {
                        JSONObject messageObject = allMessages.getJSONObject(i);
                        String sender = messageObject.getString("sender");
                        String msg = messageObject.getString("msg");

                        TextView chatTextView = new TextView(ChatActivity.this);

                        chatTextView.setTextColor(Color.parseColor("#FFFFFF"));
                        chatTextView.setTextSize(20);
                        if(sender.equals(socket.getCurrentChat())){
                            chatTextView.setLayoutParams(templateOthersMessage.getLayoutParams());
                            chatTextView.setText(templateOthersMessage.getText().toString());
                            chatTextView.setTextColor(Color.parseColor("#FFFFFF"));
                        } else {
                            chatTextView.setLayoutParams(templateOwnMessage.getLayoutParams());
                            chatTextView.setText(templateOwnMessage.getText().toString());
                            chatTextView.setTextColor(Color.parseColor("#D3D3D3"));
                        }

                        chatTextView.setId(View.generateViewId());

                        chatTextView.setText(msg);
                        linearLayout.addView(chatTextView);

                    } catch (Exception e){

                    }
                }


            }
        };
    }
}