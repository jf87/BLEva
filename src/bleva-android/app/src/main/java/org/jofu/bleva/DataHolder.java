package org.jofu.bleva;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;


public class DataHolder {
    private  ArrayList<Benchmark> benchmarks = new ArrayList<Benchmark>();
    public String BLEVA_SERVER = "http://192.168.1.139:8888";
    private final static String TAG = "DataHolder";
    public final static int MY_PERMISSIONS_REQUEST_ACCESS_FINE_LOCATION = 1;
    private Deque<Benchmark> benchmarkQueue;
    private static String macAddress = "";


    private static DataHolder instance;

    public static void initInstance() {
        instance = new DataHolder();
    }

    public static DataHolder getInstance() {
        return instance;
    }

    public ArrayList<Benchmark> getBenchmarks() {

        return benchmarks;
    }
    public void setBenchmarks(ArrayList<Benchmark> benchmarks) {
        this.benchmarks = benchmarks;
    }


    public void setBenchmark(int position, Benchmark benchmark) {
        this.benchmarks.set(position, benchmark);
    }

    public ArrayList<Benchmark> getSelectedBenchmarks() {
        ArrayList<Benchmark> selectedBenchmarks = new ArrayList<Benchmark>();
        for (int i = 0; i < benchmarks.size(); i++) {
            if (benchmarks.get(i).isSelected()) {
                selectedBenchmarks.add(benchmarks.get(i));
            }
        }
        return selectedBenchmarks;
    }

    public Deque<Benchmark> getBenchmarkQueue() {
        return benchmarkQueue;
    }

    public void setBenchmarkQueue(Deque<Benchmark> benchmarkQueue) {
        this.benchmarkQueue = benchmarkQueue;
    }

    public String getMacAddress() {
        return macAddress;
    }

    public void setMacAddress(String macAddress) {
        this.macAddress = macAddress;
    }
}
