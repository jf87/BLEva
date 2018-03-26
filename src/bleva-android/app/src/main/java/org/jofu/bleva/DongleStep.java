package org.jofu.bleva;

public class DongleStep {

    private double time;
    private String role;
    private String ble_operation;
    private String adv_data;
    private String sr_data;
    private String adv_channels;
    private String adv_interval_max;
    private String adv_interval_min;
    private String gap_connectable_mode;
    private String gap_discoverable_mode;
    private String major;
    private String minor;
    private long connection_interval_min;
    private long connection_interval_max;

    public DongleStep(double time, String role, String ble_operation, String adv_data, String sr_data, String adv_channels, String adv_interval_max, String adv_interval_min, String gap_connectable_mode, String gap_discoverable_mode, String major, String minor) {
        this.time = time;
        this.role = role;
        this.ble_operation = ble_operation;
        this.adv_data = adv_data;
        this.sr_data = sr_data;
        this.adv_channels = adv_channels;
        this.adv_interval_max = adv_interval_max;
        this.adv_interval_min = adv_interval_min;
        this.gap_connectable_mode = gap_connectable_mode;
        this.gap_discoverable_mode = gap_discoverable_mode;
        this.major = major;
        this.minor = minor;
    }

    public DongleStep() {

    }

    public double getTime() {
        return time;
    }

    public void setTime(double time) {
        this.time = time;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public String getBle_operation() {
        return ble_operation;
    }

    public void setBle_operation(String ble_operation) {
        this.ble_operation = ble_operation;
    }

    public String getAdv_data() {
        return adv_data;
    }

    public void setAdv_data(String adv_data) {
        this.adv_data = adv_data;
    }

    public String getSr_data() {
        return sr_data;
    }

    public void setSr_data(String sr_data) {
        this.sr_data = sr_data;
    }

    public String getAdv_channels() {
        return adv_channels;
    }

    public void setAdv_channels(String adv_channels) {
        this.adv_channels = adv_channels;
    }

    public String getAdv_interval_max() {
        return adv_interval_max;
    }

    public void setAdv_interval_max(String adv_interval_max) {
        this.adv_interval_max = adv_interval_max;
    }

    public String getAdv_interval_min() {
        return adv_interval_min;
    }

    public void setAdv_interval_min(String adv_interval_min) {
        this.adv_interval_min = adv_interval_min;
    }

    public String getGap_connectable_mode() {
        return gap_connectable_mode;
    }

    public void setGap_connectable_mode(String gap_connectable_mode) {
        this.gap_connectable_mode = gap_connectable_mode;
    }

    public String getGap_discoverable_mode() {
        return gap_discoverable_mode;
    }

    public void setGap_discoverable_mode(String gap_discoverable_mode) {
        this.gap_discoverable_mode = gap_discoverable_mode;
    }

    public String getMajor() {
        return major;
    }

    public void setMajor(String major) {
        this.major = major;
    }

    public String getMinor() {
        return minor;
    }

    public void setMinor(String minor) {
        this.minor = minor;
    }

    public long getConnection_interval_max() {
        return connection_interval_max;
    }

    public void setConnection_interval_max(long connection_interval_max) {
        this.connection_interval_max = connection_interval_max;
    }

    public long getConnection_interval_min() {
        return connection_interval_min;
    }

    public void setConnection_interval_min(long connection_interval_min) {
        this.connection_interval_min = connection_interval_min;
    }
}
