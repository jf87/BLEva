package org.jofu.bleva;

import android.util.Log;

import java.util.List;

import no.nordicsemi.android.support.v18.scanner.ScanResult;

//public class MyBLEScanCallback extends no.nordicsemi.android.support.v18.scanner.ScanCallback {
//
//    private static final String TAG = "MyBLEScanCallback";
//    public Benchmark benchmark;
//    public PhoneStep step;
//    public BluetoothLeService mBluetoothLeService;
//
//
//    @Override
//    public void onScanResult(int callbackType, ScanResult result) {
//        Log.d(TAG, result.toString());
//        benchmark.addResult(result);
//        if (step.getBle_operation().equals("connecing")) {
////            mBluetoothGatt = result.getDevice().connectGatt(this, false, mGattCallback);
//        }
//    }
//
//    /**
//     * Callback when batch results are delivered.
//     *å
//     * @param results List of scan results that are previously scanned.
//     */
//    @Override
//    public void onBatchScanResults(List<ScanResult> results) {
//        Log.d(TAG, results.toString());
//        benchmark.addResults(results);
//
//    }
//
//    /**
//     * Callback when scan could not be started.
//     *
//     * @param errorCode Error code (one of SCAN_FAILED_*) for scan failure.
//     */
//    @Override
//    public void onScanFailed(int errorCode) {
//        Log.e(TAG, "onScanFailed: "+errorCode);
//    }
//
//}
