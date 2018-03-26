package org.jofu.bleva;

import java.util.ArrayList;

public class Dongle {

        public Dongle(String gap_role, String gatt_role, ArrayList<DongleStep> steps, int replicas) {
            this.gap_role = gap_role;
            this.gatt_role = gatt_role;
            this.steps = steps;
            this.replicas = replicas;
        }

        public Dongle() {
        }

        private int replicas;
        private String gap_role;
        private String gatt_role;
        private ArrayList<DongleStep> steps = new ArrayList<DongleStep>();

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

        public ArrayList<DongleStep> getSteps() {
            return steps;
        }

        public void setSteps(ArrayList<DongleStep> steps) {
            this.steps = steps;
        }

        public int getReplicas() {
            return replicas;
        }

        public void setReplicas(int replicas) {
            this.replicas = replicas;
        }

        @Override
        public String toString()
        {
            String s = "/n";

            for (int i = 0; i < steps.size(); i++) {
                s = s +
                        "PhoneStep: " + i + "\n" +
                        "Time: " + steps.get(i).getTime() + "\n" +
                        "Role: " + steps.get(i).getRole() + "\n" +
                        "Ble_operation: " + steps.get(i).getBle_operation() + "\n" ;
            }
            return s;
        }

}
