package org.jofu.bleva;

import java.util.ArrayList;

public class Phone {

    public Phone(String gap_role, String gatt_role, ArrayList<PhoneStep> steps, int replicas) {
        this.gap_role = gap_role;
        this.gatt_role = gatt_role;
        this.steps = steps;
        this.replicas = replicas;
    }

    public Phone() {
    }

    private int replicas;
    private String gap_role;
    private String gatt_role;
    private ArrayList<PhoneStep> steps = new ArrayList<PhoneStep>();

    public String getGap_role() {
        return gap_role;
    }

    public void setGap_role(String gap_role) {
        this.gap_role = gap_role;
    }

    public String getGatt_role() {
        return gatt_role;
    }

    public void setGatt_role(String gatt_role) {
        this.gatt_role = gatt_role;
    }

    public ArrayList<PhoneStep> getSteps() {
        return steps;
    }

    public void setSteps(ArrayList<PhoneStep> steps) {
        this.steps = steps;
    }


    @Override
    public String toString()
    {
        String s = "/n";

        for (int i = 0; i < steps.size(); i++) {
            s = s +
                    "PhoneStep: " + i + "\n" +
                    "Time: " + steps.get(i).getTime() + "\n" +
                    "Ble_operation: " + steps.get(i).getBle_operation() + "\n" ;
        }
        return s;
    }


    public int getReplicas() {
        return replicas;
    }

    public void setReplicas(int replicas) {
        this.replicas = replicas;
    }
}
