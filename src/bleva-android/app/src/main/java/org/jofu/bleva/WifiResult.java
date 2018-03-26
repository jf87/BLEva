package org.jofu.bleva;

/**
 * Created by Jonathan Fuerst <jf@jofu.org> on 14/03/17.
 */

public class WifiResult {

    private long http_start;
    private long http_stop;
    private long latency;
    private int http_code;
    private long size;

    public long getLatency() {
        return latency;
    }

    public void setLatency(long latency) {
        this.latency = latency;
    }

    public long getHttp_stop() {
        return http_stop;
    }

    public void setHttp_stop(long http_stop) {
        this.http_stop = http_stop;
    }

    public long getHttp_start() {
        return http_start;
    }

    public void setHttp_start(long http_start) {
        this.http_start = http_start;
    }

    public int getHttp_code() {
        return http_code;
    }

    public void setHttp_code(int http_code) {
        this.http_code = http_code;
    }

    public long getSize() {
        return size;
    }

    public void setSize(long size) {
        this.size = size;
    }
}
