package org.jofu.bleva;

import java.util.ArrayList;
import java.util.List;

import no.nordicsemi.android.support.v18.scanner.ScanResult;

public class PhoneStep {
    private double time;
    private String ble_operation;
    private String scan_mode;
    private long report_delay;
    private String callback_type;
    private String match_num;
    private String match_mode;
    private String wifi_state;
    private ArrayList<String> filters = new ArrayList<String>();
    private PhoneStepResult phone_step_result = new PhoneStepResult();

    public ArrayList<String> getFilters() {
        return filters;
    }


    public void setFilters(ArrayList<String> filters) {
        this.filters = filters;
    }

    public void addFilter(String filter) {
        this.filters.add(filter);
    }

    public PhoneStepResult getPhone_step_result() {
        return phone_step_result;
    }

    public void setPhone_step_result(PhoneStepResult phone_step_result) {
        this.phone_step_result = phone_step_result;
    }

    public String getWifi_state() {
        return wifi_state;
    }

    public void setWifi_state(String wifi_state) {
        this.wifi_state = wifi_state;
    }


    public long getReport_delay() {
        return report_delay;
    }

    public void setReport_delay(long report_delay) {
        this.report_delay = report_delay;
    }

    public double getTime() {
        return time;
    }

    public void setTime(double time) {
        this.time = time;
    }

    public String getBle_operation() {
        return ble_operation;
    }

    public void setBle_operation(String ble_operation) {
        this.ble_operation = ble_operation;
    }

    public String getScan_mode() {
        return scan_mode;
    }

    public void setScan_mode(String scan_mode) {
        this.scan_mode = scan_mode;
    }

    public String getCallback_type() {
        return callback_type;
    }

    public void setCallback_type(String callback_type) {
        this.callback_type = callback_type;
    }

    public String getMatch_num() {
        return match_num;
    }

    public void setMatch_num(String match_num) {
        this.match_num = match_num;
    }

    public String getMatch_mode() {
        return match_mode;
    }

    public void setMatch_mode(String match_mode) {
        this.match_mode = match_mode;
    }

}