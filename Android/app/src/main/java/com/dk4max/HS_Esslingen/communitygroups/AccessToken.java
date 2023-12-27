package com.dk4max.HS_Esslingen.communitygroups;

import com.google.gson.annotations.SerializedName;
public class AccessToken {
    @SerializedName("access_token")
    private String accessToken;
    @SerializedName("expires_in")
    private Integer expiresIn;
    @SerializedName("refresh_expires_in")
    private Integer refresh_expires_in;
    @SerializedName("refresh_token")
    private String refresh_token;
    @SerializedName("token_type")
    private String tokenType;
    @SerializedName("id_token")
    private String idToken;
    @SerializedName("not-before-policy")
    private Integer notBeforePolicy;
    @SerializedName("session_state")
    private String sessionState;
    @SerializedName("scope")
    private String scope;

    public AccessToken(String accesToken, Integer expiresIn) {
        this.accessToken = accesToken;
        this.expiresIn = expiresIn;
    }

    protected String getAccessToken(){
        return accessToken;
    }

}
