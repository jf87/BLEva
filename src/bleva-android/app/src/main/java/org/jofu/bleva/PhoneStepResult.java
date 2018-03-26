package org.jofu.bleva;

import java.util.ArrayList;
import java.util.List;

import no.nordicsemi.android.support.v18.scanner.ScanResult;

public class PhoneStepResult {
    private double startTime;

    private ArrayList<ScanResult> scan_results = new ArrayList<ScanResult>();
    private ArrayList<GattResult> gatt_results = new ArrayList<GattResult>();
    private ArrayList<WifiResult> wifi_results = new ArrayList<WifiResult>();


    public double getStartTime() {
        return startTime;
    }
    public void setStartTime(double startTime) {
        this.startTime = startTime;
    }

    public ArrayList<ScanResult> getScanResults() {
        return scan_results;
    }

    public void setScanResults(ArrayList<ScanResult> scan_results) {
        this.scan_results = scan_results;
    }

    public void addResult(ScanResult result) {
        this.scan_results.add(result);
    }

    public void addResults(List<ScanResult> results) {
        this.scan_results.addAll(results);
    }


    public void addWiFiResult(WifiResult result) {
        this.wifi_results.add(result);
    }

    public ArrayList<GattResult> getGattResults() {
        return gatt_results;
    }

    public void setGattResults(ArrayList<GattResult> gattResults) {
        this.gatt_results = gattResults;
    }

    public GattResult getCurrentGattResult() {
        GattResult mgattResult;
        if (this.gatt_results.isEmpty()) {
            mgattResult = new GattResult();
            this.gatt_results.add(mgattResult);
        } else {
            mgattResult = this.gatt_results.get(0); //FIXME not always 0
        }
        return mgattResult;
    }


    public void addTimeConnectedGattResult(long t_connect) {
        GattResult mgattResult = getCurrentGattResult();
        mgattResult.setTime_connected(t_connect);
    }

    public void addTimeServicesDiscoverdGattResult(long t_services) {
        GattResult mgattResult = getCurrentGattResult();
        mgattResult.setTime_services_discovered(t_services);
    }

    public void addTimeConnectingGattResult(long t_connecting) {
        GattResult mgattResult = getCurrentGattResult();
        mgattResult.setTime_connecting(t_connecting);
    }

    public void addTimeDisconnectedGattResult(long t_disconnect) {
        GattResult mgattResult = getCurrentGattResult();

        mgattResult.setTime_disconnected(t_disconnect);
    }

    public void addTimeReadRequestStartGattResult(long t_read_start) {
        GattResult mgattResult = getCurrentGattResult();
        mgattResult.setTime_read_request_start(t_read_start);
    }

    public void addTimeReadRequestDoneGattResult(long t_read_done) {
        GattResult mgattResult = getCurrentGattResult();
        mgattResult.setTime_read_request_done(t_read_done);
    }


    public void addTimeWriteRequestStartGattResult(long t_write_start) {
        GattResult mgattResult = getCurrentGattResult();
        mgattResult.setTime_write_request_start(t_write_start);
    }

    public void addTimeWriteRequestDoneGattResult(long t_write_done) {
        GattResult mgattResult = getCurrentGattResult();
        mgattResult.setTime_write_request_done(t_write_done);
    }

    public ArrayList<WifiResult> getWifi_results() {
        return wifi_results;
    }

    public void setWifi_results(ArrayList<WifiResult> wifi_results) {
        this.wifi_results = wifi_results;
    }
}
