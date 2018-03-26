package org.jofu.bleva;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Log;

import com.android.volley.DefaultRetryPolicy;
import com.android.volley.NetworkResponse;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.JsonRequest;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;

import javax.net.ssl.HttpsURLConnection;

public class NetManager {

    private static final String TAG = "NetManager";
    private static NetManager instance = null;

    //for Volley API
    public RequestQueue requestQueue;

    private NetManager(Context context)
    {
        requestQueue = Volley.newRequestQueue(context.getApplicationContext());
    }

    public static void initInstance(Context context) {
        instance = new NetManager(context);
    }

    //this is so you don't need to pass context each time
    public static synchronized NetManager getInstance()
    {
        if (null == instance)
        {
            throw new IllegalStateException(NetManager.class.getSimpleName() +
                    " is not initialized, call getInstance(...) first");
        }
        return instance;
    }

    public void GETStringRequest(String URL, final GETListener<String> listener) {
        StringRequest stringRequest = new StringRequest(Request.Method.GET, URL,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        listener.onSuccess(response);
                    }
                }, new Response.ErrorListener() {

            @Override
            public void onErrorResponse(VolleyError error) {
                if (null != error.networkResponse)
                {
                    Log.d(TAG + ": ", "Error Response code: " + error.networkResponse.statusCode);
                    listener.onFail(error);
                }
            }
        });
        requestQueue.add(stringRequest);
    }


    public void GETRequest(String URL, final GETListener<JSONArray> listener) {
        JsonArrayRequest request = new JsonArrayRequest(Request.Method.GET,URL,null,
                new Response.Listener<JSONArray>() {
                    @Override
                    public void onResponse(JSONArray response) {
                        listener.onSuccess(response);
                    }
                }, new Response.ErrorListener() {

            @Override
            public void onErrorResponse(VolleyError error) {
                if (null != error.networkResponse)
                {
                    Log.d(TAG + ": ", "Error Response code: " + error.networkResponse.statusCode);
                    listener.onFail(error);
                }
            }
        });

        requestQueue.add(request);
    }

    // this works very bad, just stucks if there is no route to host...
    public void POSTRequest(String URL, JSONObject body, final POSTListener<JSONObject> listener) {
        JsonObjectRequest request = new JsonObjectRequest(Request.Method.POST, URL, body,

                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        listener.onSuccess(response);
                    }
                }, new Response.ErrorListener() {

            @Override
            public void onErrorResponse(VolleyError error) {
                if (null != error.networkResponse)
                {
                    Log.d(TAG + ": ", "Error Response code: " + error.networkResponse.statusCode);
                    listener.onFail(error);
                }
            }

        })
        {
            @Override
            public Priority getPriority() {
                return Priority.HIGH;
            }
        };
        Log.d(TAG, request.toString());
        Log.d(TAG, requestQueue.toString());
        request.setRetryPolicy(new DefaultRetryPolicy(5000,
                DefaultRetryPolicy.DEFAULT_MAX_RETRIES,
                DefaultRetryPolicy.DEFAULT_BACKOFF_MULT));
        requestQueue.add(request);
        requestQueue.start();
    }

    public class POSTTask extends AsyncTask<Void, Void, String> {

        String url;
        String body;
        POSTListener<String> listener;

        POSTTask(String url, String body, POSTListener<String> listener){
            this.url = url;
            this.body = body;
            this.listener = listener;
        }

        @Override
        protected String doInBackground(Void... arg0) {
            return performPostCall(this.url, this.body);
        }

        @Override
        protected void onPostExecute(String result) {
            super.onPostExecute(result);
            listener.onSuccess(result);
        }
    }

    public String performPostCall(String requestURL, String body) {
        URL url;
        String response = "";
        try {
            url = new URL(requestURL);

            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setReadTimeout(60000);
            conn.setConnectTimeout(60000);
            conn.setRequestMethod("POST");
            conn.setDoInput(true);
            conn.setDoOutput(true);


            OutputStream os = conn.getOutputStream();
            BufferedWriter writer = new BufferedWriter(
                    new OutputStreamWriter(os, "UTF-8"));
            writer.write(body);
            writer.flush();
            writer.close();
            os.close();
            int responseCode=conn.getResponseCode();

            if (responseCode == HttpsURLConnection.HTTP_OK) {
                String line;
                BufferedReader br=new BufferedReader(new InputStreamReader(conn.getInputStream()));
                while ((line=br.readLine()) != null) {
                    response+=line;
                }
            }
            else {
                Log.d(TAG, "RESPONSE CODE "+responseCode);
                response="";
            }
        } catch (Exception e) {
            Log.d(TAG, "Exception "+e.toString());
            response = "401";
            return response;
        }

        return response;
    }

    // for performing wifi simulations
    public WifiResult performGetCall(String requestURL) {
        URL url;
        StringBuffer response = new StringBuffer();
        WifiResult wr = new WifiResult();
        long t0 = System.currentTimeMillis();
        wr.setHttp_start(t0);
        try {
            url = new URL(requestURL);

            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setReadTimeout(20000);
            conn.setConnectTimeout(20000);
            conn.setRequestMethod("GET");
            conn.setRequestProperty("User-Agent", "Mozilla / 5.0");
            BufferedReader in = new BufferedReader(
                    new InputStreamReader(conn.getInputStream()));
            String inputLine;

            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();
            long size = response.length();
            long t1 = System.currentTimeMillis();
            int responseCode = conn.getResponseCode();
            wr.setHttp_code(responseCode);
            wr.setHttp_stop(t1);
            wr.setSize(size);
            if (responseCode == HttpsURLConnection.HTTP_OK) {
                Log.d(TAG, "RESPONSE CODE "+responseCode);
            }
            else {
                Log.d(TAG, "RESPONSE CODE "+responseCode);
            }


        } catch (Exception e) {
            Log.d(TAG, "RESPONSE CODE "+response.toString());
            long t1 = System.currentTimeMillis();
            wr.setHttp_code(500);
            wr.setHttp_stop(t1);
        }
        response = null;
        return wr;
    }

}