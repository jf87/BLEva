package org.jofu.bleva;

import org.json.JSONException;
import org.json.JSONObject;

public class GattResult {
    private long time_connecting;
    private long time_connected;
    private long time_services_discovered;
    private long time_disconnected;
    private long time_read_request_start;
    private long time_read_request_done;
    private long time_write_request_start;
    private long time_write_request_done;


    public long getTime_connecting() {
        return time_connecting;
    }

    public void setTime_connecting(long time_connecting) {
        this.time_connecting = time_connecting;
    }


    public long getTime_connected() {
        return time_connected;
    }

    public void setTime_connected(long time_connected) {
        this.time_connected = time_connected;
    }

    public JSONObject toJSON(){

        JSONObject jsonObject= new JSONObject();
        try {
            jsonObject.put("time_connecting", getTime_connecting());
            jsonObject.put("time_connected", getTime_connected());
            jsonObject.put("time_services_discovered", getTime_services_discovered());
            jsonObject.put("time_disconnected",getTime_disconnected());
            jsonObject.put("time_read_request_start", getTime_read_request_start());
            jsonObject.put("time_read_request_done", getTime_read_request_done());
            jsonObject.put("time_write_request_start", getTime_write_request_start());
            jsonObject.put("time_write_request_done", getTime_write_request_done());

        } catch (JSONException e) {
            e.printStackTrace();
        }
        return jsonObject;
    }

    public long getTime_services_discovered() {
        return time_services_discovered;
    }

    public void setTime_services_discovered(long time_services_discovered) {
        this.time_services_discovered = time_services_discovered;
    }

    public long getTime_disconnected() {
        return time_disconnected;
    }

    public void setTime_disconnected(long time_disconnected) {
        this.time_disconnected = time_disconnected;
    }

    public long getTime_read_request_start() {
        return time_read_request_start;
    }

    public void setTime_read_request_start(long time_read_request_start) {
        this.time_read_request_start = time_read_request_start;
    }

    public long getTime_read_request_done() {
        return time_read_request_done;
    }

    public void setTime_read_request_done(long time_read_request_done) {
        this.time_read_request_done = time_read_request_done;
    }

    public long getTime_write_request_start() {
        return time_write_request_start;
    }

    public void setTime_write_request_start(long time_write_request_start) {
        this.time_write_request_start = time_write_request_start;
    }

    public long getTime_write_request_done() {
        return time_write_request_done;
    }

    public void setTime_write_request_done(long time_write_request_done) {
        this.time_write_request_done = time_write_request_done;
    }
}
