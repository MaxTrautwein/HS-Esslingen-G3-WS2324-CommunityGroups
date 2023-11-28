package com.dk4max.HS_Esslingen.communitygroups;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import androidx.fragment.app.Fragment;

import org.json.JSONException;
import org.json.JSONObject;

import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.emitter.Emitter;

public class Tab2Fragment extends Fragment {

    private EditText editText;
    private Button buttonDisplay;
    private TextView textViewDisplay;

    public Tab2Fragment() {
        // Required empty public constructor
    }

    private Socket mSocket;
    {
        try {
            mSocket = IO.socket("http://85.215.34.151:5000");
        } catch (Exception e) {
        }

    }

    private Emitter.Listener onNewMessage = new Emitter.Listener() {
        @Override
        public void call(final Object... args) {
            getActivity().runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    JSONObject data = (JSONObject) args[0];
                    String username;
                    String message;
                    try {
                        message = data.getString("message");
                    } catch (Exception e) {
                        return;
                    }

                    // add the message to view
                    displayText(message);
                }
            });
        }
    };

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        mSocket.on("message chat 2", onNewMessage);
        mSocket.connect();
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        mSocket.disconnect();
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View view = inflater.inflate(R.layout.fragment_tab1, container, false);

        editText = view.findViewById(R.id.editTextTab1);
        buttonDisplay = view.findViewById(R.id.buttonDisplayTab1);
        textViewDisplay = view.findViewById(R.id.textViewDisplayTab1);

        buttonDisplay.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                attemptSend();
            }
        });

        return view;
    }

    private void attemptSend() {
        String message = editText.getText().toString();

        editText.setText("");
        try {
            JSONObject messageJson = new JSONObject();
            messageJson.put("message", message);
            mSocket.emit("new chat message 2", messageJson);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    private void displayText(String message) {
        textViewDisplay.setText("User 1 " + message);
    }
}
