package org.jofu.bleva;


import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.util.ArrayList;

public class Benchmark {

    private String name;
    private String description;
    private double time;
    private int repetitions;
    private Phone phone;
    private ArrayList<Dongle> dongles = new ArrayList<Dongle>();
    private BenchmarkResult benchmark_result = new BenchmarkResult();


    private transient String jsonOriginal;

    private transient boolean selected;
    private transient int activeStep;

    public ArrayList<Dongle> getDongles() {
        return dongles;
    }

    public void setDongles(ArrayList<Dongle> dongles) {
        this.dongles = dongles;
    }

    public int getActiveStep() {
        return activeStep;
    }

    public void setActiveStep(int activeStep) {
        this.activeStep = activeStep;
    }

    public int getRepetitions() {
        return repetitions;
    }

    public void setRepetitions(int repetitions) {
        this.repetitions = repetitions;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public double getTime() {
        return time;
    }

    public void setTime(double time) {
        this.time = time;
    }

    public Phone getPhone() {
        return phone;
    }

    public void setPhone(Phone phone) {
        this.phone = phone;
    }

    public boolean isSelected() {
        return selected;
    }

    public void setSelected(boolean selected) {
        this.selected = selected;
    }

    @Override
    public String toString() {
        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        return gson.toJson(this);
    }


    public boolean lastStep() {
        if (!(this.getPhone().getSteps().size() > activeStep + 1)) {
            return true;
        }
        return false;
    }

    public BenchmarkResult getBenchmark_result() {
        return benchmark_result;
    }

    public void setBenchmark_result(BenchmarkResult benchmark_result) {
        this.benchmark_result = benchmark_result;
    }

    public String getJsonOriginal() {
        return jsonOriginal;
    }

    public void setJsonOriginal(String jsonOriginal) {
        this.jsonOriginal = jsonOriginal;
    }

    public void resetAllBenchmarkReults() {
        benchmark_result = new BenchmarkResult();
        for (PhoneStep ps: phone.getSteps()) {
            PhoneStepResult phone_step_result = new PhoneStepResult();
            ps.setPhone_step_result(phone_step_result);
        }
    }
}