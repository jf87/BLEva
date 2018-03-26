package org.jofu.bleva;

import android.net.wifi.ScanResult;

import org.json.JSONArray;

import java.util.ArrayList;
import java.util.List;

public class BenchmarkResult {

    private String model_name;
    private String device_id;
    private String mac_address;
    private String api_version;
    private long start_time;
    private List <android.net.wifi.ScanResult> wifi_results;
    private float start_battery_level;
    private float stop_battery_level;



    public String getModel_name() {
        return model_name;
    }

    public void setModel_name(String model_name) {
        this.model_name = model_name;
    }

    public String getApi_version() {
        return api_version;
    }

    public void setApi_version(String api_version) {
        this.api_version = api_version;
    }

    public long getStart_time() {
        return start_time;
    }

    public void setStart_time(long start_time) {
        this.start_time = start_time;
    }

    public List<ScanResult> getWifi_results() {
        return wifi_results;
    }

    public void setWifi_results(List<ScanResult> wifi_results) {
        this.wifi_results = wifi_results;
    }

    public float getStart_battery_level() {
        return start_battery_level;
    }

    public void setStart_battery_level(float start_battery_level) {
        this.start_battery_level = start_battery_level;
    }

    public float getStop_battery_level() {
        return stop_battery_level;
    }

    public void setStop_battery_level(float stop_battery_level) {
        this.stop_battery_level = stop_battery_level;
    }

    public String getDevice_id() {
        return device_id;
    }

    public void setDevice_id(String device_id) {
        this.device_id = device_id;
    }

    public String getMac_address() {
        return mac_address;
    }

    public void setMac_address(String mac_address) {
        this.mac_address = mac_address;
    }
}
