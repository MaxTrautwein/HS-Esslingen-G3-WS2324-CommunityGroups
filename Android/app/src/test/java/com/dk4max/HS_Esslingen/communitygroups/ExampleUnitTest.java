package com.dk4max.HS_Esslingen.communitygroups;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.MockedStatic;
import org.mockito.Mockito;
import org.mockito.MockitoAnnotations;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import java.io.IOException;

import retrofit2.Call;
import retrofit2.Response;

public class ExampleUnitTest {

    @Mock
    private GetDataService mockGetDataService;
    @Mock
    private Call<AccessToken> mockCall;
    @Mock
    private Response<AccessToken> mockResponse;

   public MainActivity activity;

    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);

        activity = new MainActivity();

        activity.etUsername = Mockito.mock(EditText.class);
        activity.etPassword = Mockito.mock(EditText.class);
        activity.btnLogin = Mockito.mock(Button.class);


        when(activity.etUsername.getText().toString()).thenReturn("validUser");
        when(activity.etPassword.getText().toString()).thenReturn("validPassword");
        when(mockGetDataService.getAccessToken(Mockito.anyString(), Mockito.anyString(), Mockito.anyString(), Mockito.anyString(), Mockito.anyString(), Mockito.anyString())).thenReturn(mockCall);
    }

    @Test
    public void login_withValidCredentials_shouldAttemptAccess() throws IOException {

        when(mockResponse.isSuccessful()).thenReturn(true);
        when(mockCall.execute()).thenReturn(mockResponse);


        activity.getAccessToken();


        verify(mockGetDataService).getAccessToken("AppLogin", "password", "client_secret", "openid", "validUser", "validPassword");
    }

    @Test
    public void login_withInvalidCredentials_shouldShowToast() throws IOException {

        when(mockResponse.isSuccessful()).thenReturn(false);
        when(mockCall.execute()).thenReturn(mockResponse);


        activity.getAccessToken();


        try (MockedStatic<Toast> mockedToast = Mockito.mockStatic(Toast.class)) {
            activity.getAccessToken();
            mockedToast.verify(() -> Toast.makeText(Mockito.any(), Mockito.eq("Errortest1243"), Mockito.anyInt()), Mockito.times(1));
        }
    }
}