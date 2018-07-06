package org.jofu.bleva;

import android.annotation.TargetApi;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.app.AlarmManager;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattService;
import android.content.BroadcastReceiver;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.ServiceConnection;
import android.media.RingtoneManager;
import android.net.Uri;
import android.net.wifi.WifiManager;
import android.os.BatteryManager;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.os.Looper;
import android.os.Message;
import android.os.PowerManager;
import android.os.SystemClock;
import android.provider.Settings;
import android.util.Log;
import android.widget.Toast;
import android.os.Process;

import com.google.gson.Gson;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.InetAddress;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import no.nordicsemi.android.support.v18.scanner.BluetoothLeScannerCompat;
import no.nordicsemi.android.support.v18.scanner.ScanFilter;
import no.nordicsemi.android.support.v18.scanner.ScanResult;
import no.nordicsemi.android.support.v18.scanner.ScanSettings;

import static java.security.AccessController.getContext;


@TargetApi(18)
public class BenchmarkService extends Service {

    private final static String TAG = "BenchmarkService";

    private boolean POWER_MEASUREMENT = false;

    //threading
    private Handler BLEHandler;
    private ExecutorService pool;
    private boolean Running; //just to make sure that we really don't have two benchmark threads at the same time
    public Deque<Benchmark> benchmarkQueue; // the benchmarks we schedule to run

    //wifi
    private WifiManager wifiManager;
    private List<android.net.wifi.ScanResult> wifiResults;
    private WifiBroadcastReceiver mWifiBroadcastReceiver;


    //GATT
    private BluetoothLeService mBluetoothLeService;
    private GattBroadcastReceiver mGattBroadcastReceiver;
    private HashMap<String, BluetoothGattCharacteristic> allChars;
    private HashMap<String, BluetoothDevice> mLeDevices;
    private boolean mConnected = false;



    private Looper mServiceLooper;
    private ServiceHandler mServiceHandler;
    final Context context = this;
    private boolean  rescanning = true;

    // Code to manage Service lifecycle.
    private final ServiceConnection mServiceConnection = new ServiceConnection() {

        @Override
        public void onServiceConnected(ComponentName componentName, IBinder service) {
            mBluetoothLeService = ((BluetoothLeService.LocalBinder) service).getService();
            if (!mBluetoothLeService.initialize()) {
                Log.e(TAG, "Unable to initialize Bluetooth");
            }
        }

        @Override
        public void onServiceDisconnected(ComponentName componentName) {
            mBluetoothLeService = null;
        }
    };


    // Handler that receives messages from the thread
    private final class ServiceHandler extends Handler {
        public ServiceHandler(Looper looper) {
            super(looper);
        }
        @Override
        public void handleMessage(Message msg) {
            try {
                benchmarkQueue = DataHolder.getInstance().getBenchmarkQueue();

            } catch (Exception e) {
                e.printStackTrace();
                stopSelf();

            }
            try {
                Benchmark b_run = benchmarkQueue.peekFirst();
                if (b_run != null) {
                    schedulePreBenchmark(b_run);
                } else {
                    Log.d(TAG, "No Benchmarks selected");
                }
            } catch (Exception e) {
                stopSelf();
            }
            // Stop the service using the startId, so that we don't stop
            // the service in the middle of handling another job
//                stopSelf(msg.arg1);
        }
    }

    @Override
    public void onCreate() {
        // Start up the thread running the service.  Note that we create a
        // separate thread because the service normally runs in the process's
        // main thread, which we don't want to block.  We also make it
        // background priority so CPU-intensive work will not disrupt our UI.
        HandlerThread thread = new HandlerThread("ServiceStartArguments",
                Process.THREAD_PRIORITY_BACKGROUND);
        thread.start();

        // make sure wifi is on
        wifiManager = (WifiManager) this.getSystemService(Context.WIFI_SERVICE);
        boolean wifiEnabled = wifiManager.isWifiEnabled();
        if (!wifiEnabled) {
            wifiManager.setWifiEnabled(true);
        }

        Intent gattServiceIntent = new Intent(this, BluetoothLeService.class);
        bindService(gattServiceIntent, mServiceConnection, BIND_AUTO_CREATE);
        mLeDevices = new HashMap<String, BluetoothDevice>();

        // resetting BLE adapter to begin
        Util.resetBluetoothAdapter();

        pool = Executors.newSingleThreadExecutor();
        BLEHandler = new Handler();


        // Get the HandlerThread's Looper and use it for our Handler
        mServiceLooper = thread.getLooper();
        mServiceHandler = new ServiceHandler(mServiceLooper);

//        testAlarm(10000);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Toast.makeText(this, "service starting", Toast.LENGTH_SHORT).show();

        // For each start request, send a message to start a job and deliver the
        // start ID so we know which request we're stopping when we finish the job
        Message msg = mServiceHandler.obtainMessage();
        msg.arg1 = startId;
        mServiceHandler.sendMessage(msg);

        // If we get killed, after returning from here, restart
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        // We don't provide binding, so return null
        return null;
    }

    @Override
    public void onDestroy() {
        if (mWifiBroadcastReceiver != null) {
            try {
                unregisterReceiver(mWifiBroadcastReceiver);
            } catch (IllegalArgumentException e) {
                Log.w(TAG, "mWifiBroadcastReceiver not registered, should not matter...");
            }
        }
        unbindService(mServiceConnection);
        boolean wifiEnabled = wifiManager.isWifiEnabled();
        if (!wifiEnabled) {
            wifiManager.setWifiEnabled(true);
        }
        Toast.makeText(this, "service done", Toast.LENGTH_SHORT).show();
        super.onDestroy();
    }

    void testAlarm(long period) {
        PendingIntent alarmIntent;
        Intent intent = new Intent(this, AlarmReceiver.class);
        alarmIntent = PendingIntent.getBroadcast(this, 0, intent, 0);
        AlarmManager am;
        am = (AlarmManager) this.getSystemService(Context.ALARM_SERVICE);
        am.setWindow(AlarmManager.ELAPSED_REALTIME_WAKEUP, SystemClock.elapsedRealtime() + period, 500, alarmIntent);
    }

    public void schedulePreBenchmark(final Benchmark b) {
        mWifiBroadcastReceiver = new WifiBroadcastReceiver(b);
        registerReceiver(mWifiBroadcastReceiver, new IntentFilter(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION));
        wifiManager.startScan();
    }



    public void scheduleNextBenchmark(final Benchmark b) {
        new Thread(new Runnable() {
            public void run() {
                Uri alarmSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);

                Notification n  = new Notification.Builder(context)
                        .setContentTitle("START")
                        .setSmallIcon(android.R.drawable.arrow_up_float)
                        .setContentText(b.getName()).setPriority(Notification.PRIORITY_MAX).build(); //setSound(alarmSound).build();


                NotificationManager notificationManager =
                        (NotificationManager) getSystemService(NOTIFICATION_SERVICE);

                notificationManager.notify(0, n);

                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }

                notificationManager.notify(0, n);


                int activeStep = b.getActiveStep();
                //first step means we need to post the benchmark and then sync
                if (activeStep == 0) {
                    //apparently adapter does not like to get resetted to often...
                    // Util.resetBluetoothAdapter();
                    while (!BluetoothAdapter.getDefaultAdapter().isEnabled()) {
                        Log.d(TAG, "BLE not enabled yet...");
                        try {
                            Thread.sleep(1000);
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                        if (!BluetoothAdapter.getDefaultAdapter().isEnabled()) {
                            BluetoothAdapter.getDefaultAdapter().enable();
                        }
                    }
                    if (!POWER_MEASUREMENT) {
                        // FIXME this is not good for multiple phones
                        Log.d(TAG, "waiting for sucessful post");
                        boolean post = postBenchmark(b);
//                        while (!post) {
//                            Log.d(TAG, "waiting for sucessful post");
//                            post = postBenchmark(b);
//                        }
                        if (post) {
                            Log.d(TAG, "Successfully posted");

                        } else {
                            // FIXME stop here
                            stopBenchmark();
                        }
                        Log.d(TAG, "waiting for sucessful sync");

                        boolean sync = postBenchmarkSync(b);
                        if (sync) {
                            Log.d(TAG, "Successfully synced");

                        } else {
                            stopBenchmark();
                            // FIXME stop here

                        }
//                        while (!sync) {
//                            Log.d(TAG, "waiting for sucessful sync");
//                            sync = postBenchmarkSync(b);
//                            try {
//                                Thread.sleep(1000);
//                            } catch (InterruptedException e) {
//                                e.printStackTrace();
//                            }
//                        }
                    }
                    try {
                        b.getBenchmark_result().setApi_version(Integer.toString(android.os.Build.VERSION.SDK_INT));
                    } catch (Exception e) {
                        e.printStackTrace();
                        b.getBenchmark_result().setApi_version("unknown");
                    }
                    try {
                        b.getBenchmark_result().setModel_name(Util.getDeviceName());
                    } catch (Exception e) {
                        e.printStackTrace();
                        b.getBenchmark_result().setModel_name("unknown");
                    }

                    try {
                        String myAndroidDeviceId = Settings.Secure.getString(getApplicationContext().getContentResolver(), Settings.Secure.ANDROID_ID);
                        b.getBenchmark_result().setDevice_id(myAndroidDeviceId);

                    } catch (Exception e) {
                        b.getBenchmark_result().setDevice_id("unknown");
                    }

                    try {
                        String macA = DataHolder.getInstance().getMacAddress();
                        b.getBenchmark_result().setMac_address(macA);

                    } catch (Exception e) {
                        b.getBenchmark_result().setMac_address("unknown");

                    }



                    try {
                        b.getBenchmark_result().setStart_time(System.currentTimeMillis());
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                    try {
                        b.getBenchmark_result().setStart_battery_level(getBatteryLevel());
                    } catch (Exception e) {
                        e.printStackTrace();
                    }

//                    n  = new Notification.Builder(context)
//                            .setContentTitle("Battery Begin")
//                            .setSmallIcon(android.R.drawable.ic_lock_idle_charging)
//                            .setContentText(Float.toString(b.getBenchmark_result().getStart_battery_level())).build();
//                    notificationManager.notify(0, n);



                    scheduleNextStep(b);
                }
            }
        }).start();
    }

    public void scheduleNextStep(final Benchmark b) {
        new Thread(new Runnable() {
            public void run() {
                try {
                    runStep(b);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }

    public void runStep(final Benchmark b) throws InterruptedException {
        while (Running) {
            //busy waiting for other benchmark, this should never happen!
            try {
                Thread.sleep(100);
                Log.d(TAG, "SLEEPING, SOMETHING IS WRONG");
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        Running = true;
        int activeStep = b.getActiveStep();

        Log.d(TAG, "NOW RUNNING: " + b.getName() + " STEP: " + activeStep);
        Phone p = b.getPhone();

        // parse instructions
        if (p.getGap_role().equals("observer") || p.getGap_role().equals("central")) {
            Log.d(TAG, "step in running:" + b.getActiveStep());
            PhoneStep s = p.getSteps().get(activeStep);
            if (s.getBle_operation().equals("scanning")) {
                int scan_mode = 0;
                switch (s.getScan_mode()) {
                    case "balanced":
                        scan_mode = ScanSettings.SCAN_MODE_BALANCED;
                        break;
                    case "low_latency":
                        scan_mode = ScanSettings.SCAN_MODE_LOW_LATENCY;
                        break;
                    case "low_power":
                        scan_mode = ScanSettings.SCAN_MODE_LOW_POWER;
                        break;
                    case "opportunistic":
                        scan_mode = ScanSettings.SCAN_MODE_OPPORTUNISTIC;
                        break;
                    case "bluemorpho":
                        scan_mode = ScanSettings.SCAN_MODE_LOW_LATENCY;
                        break;
                    default:
                        scan_mode = ScanSettings.SCAN_MODE_BALANCED;
                }
                long report_delay = s.getReport_delay();
                int match_num = 0;
                switch (s.getMatch_num()) {
                    case "one_advertisement":
                        match_num = ScanSettings.MATCH_NUM_ONE_ADVERTISEMENT;
                        break;
                    case "few_advertisement":
                        match_num = ScanSettings.MATCH_NUM_FEW_ADVERTISEMENT;
                        break;
                    case "max_advertisement":
                        match_num = ScanSettings.MATCH_NUM_MAX_ADVERTISEMENT;
                        break;
                    default:
                        match_num = ScanSettings.MATCH_NUM_FEW_ADVERTISEMENT;

                }
                int match_mode = 0;
                switch (s.getMatch_mode()) {
                    case "sticky":
                        match_mode = ScanSettings.MATCH_MODE_STICKY;
                        break;
                    case "aggressive":
                        match_mode = ScanSettings.MATCH_MODE_AGGRESSIVE;
                        break;
                    default:
                        match_mode = ScanSettings.MATCH_MODE_STICKY;

                }
                int callbackType = 0;
                switch (s.getCallback_type()) {
                    case "first_match":
                        callbackType = ScanSettings.CALLBACK_TYPE_FIRST_MATCH;
                        break;
                    case "all_matches":
                        callbackType = ScanSettings.CALLBACK_TYPE_ALL_MATCHES;
                        break;
                    case "match_lost":
                        callbackType = ScanSettings.CALLBACK_TYPE_MATCH_LOST;
                        break;
                    default:
                        callbackType = ScanSettings.CALLBACK_TYPE_ALL_MATCHES;

                }
                List<ScanFilter> filters = new ArrayList<>();

                if (!s.getFilters().isEmpty()) {
                    for (int j=0;j<s.getFilters().size();j++) {
                        Log.d(TAG, "Added filter: " +s.getFilters().get(j));
                        filters.add(new ScanFilter.Builder().setDeviceName(s.getFilters().get(j)).build());
                    }
                } else {
                    filters = null;

                }
                final ScanSettings settings = new ScanSettings.Builder()
                        .setScanMode(scan_mode).setReportDelay(report_delay).setCallbackType(callbackType).setMatchMode(match_mode)
                        .setUseHardwareBatchingIfSupported(false).build();
                Log.d(TAG, "scan_mode: " + scan_mode);
                Log.d(TAG, "match_num: " + match_num);
                Log.d(TAG, "match_mode: " + match_mode);
                Log.d(TAG, "callbackType: " + callbackType);
                final BluetoothLeScannerCompat scanner = BluetoothLeScannerCompat.getScanner();
                final MyBLEScanCallback c = new MyBLEScanCallback();
//                    b.setActiveStep(activeStep);
                c.benchmark = b;
                c.step = s;
                boolean wifiEnabled = wifiManager.isWifiEnabled();
                if (s.getWifi_state().equals("off") && wifiEnabled) {
                    wifiManager.setWifiEnabled(false);
                } else if (s.getWifi_state().equals("on") && !wifiEnabled) {
                    wifiManager.setWifiEnabled(true);
                } else if (s.getWifi_state().equals("active")) {
                    //simulate wifi usage
                    pool.execute(new WifiActiveService(b));

                }
                c.filters = filters;
                c.settings = settings;
                c.scanner = scanner;
                scanLeDevice(true, filters, scanner, settings, c, (int) s.getTime());

            } else if (s.getBle_operation().equals("connecting")) {
                // connect to device in filter
                Log.d(TAG, "connecting");
                if (!s.getFilters().isEmpty()) {
                    for (int j=0;j<s.getFilters().size();j++) {
                        s.getFilters().get(j);
                        BluetoothDevice ble_device = mLeDevices.get(s.getFilters().get(j));
                        if (ble_device != null) {
                            Log.d(TAG, "ble_device " + ble_device.toString());
                            String ble_address = ble_device.getAddress();
                            mGattBroadcastReceiver = new GattBroadcastReceiver(b);
                            try {
                                unregisterReceiver(mGattBroadcastReceiver); //just in case...
                            } catch (IllegalArgumentException e) {
                                Log.w(TAG, "mGattBroadcastReceiver not registered, should not matter...");
                            }
                            registerReceiver(mGattBroadcastReceiver, makeGattUpdateIntentFilter());
                            Log.d(TAG, "creating connection");
                            if (mBluetoothLeService != null) {
                                long t_connect = System.currentTimeMillis();
                                GattResult mgattResult;
                                if (b.getPhone().getSteps().get(b.getActiveStep()).getPhone_step_result().getGattResults().isEmpty()) {
                                    mgattResult = new GattResult();
                                    mgattResult.setTime_connecting(t_connect);
                                    b.getPhone().getSteps().get(b.getActiveStep()).getPhone_step_result().getGattResults().add(mgattResult);

                                } else {
                                    mgattResult = b.getPhone().getSteps().get(b.getActiveStep()).getPhone_step_result().getGattResults().get(0); //FIXME not always 0
                                    mgattResult.setTime_connecting(t_connect);
                                }
                                final boolean result = mBluetoothLeService.connect(ble_address);
                                Log.d(TAG, "Connect request result=" + result);
                            }
                        } else {
                            Log.e(TAG, "Did not find our device :(");
                            restartBenchmark();
                        }
                    }
                } else {
                    Log.d(TAG, "No filters set...");

                }
            } else if (s.getBle_operation().equals("service_discovery")) {
                Log.e(TAG, "service_discovery");
                if (mBluetoothLeService != null && mConnected) {
                    mBluetoothLeService.discoverServices();
                } else {
                    Log.e(TAG, "NOT CONNECTED");
                    restartBenchmark();
                }
            } else if (s.getBle_operation().equals("read_characteristic")) {
                Log.e(TAG, "read_characteristic");
                if (mBluetoothLeService != null && mConnected) {
                    String mUuid = s.getFilters().get(0); //FIXME just first element for now
                    Log.e(TAG, "mUuid:" + mUuid);
                    if (allChars.containsKey(mUuid)) {
                        BluetoothGattCharacteristic mChar = allChars.get(mUuid);
                        long t_read_char = System.currentTimeMillis();
                        s.getPhone_step_result().addTimeReadRequestStartGattResult(t_read_char);
                        mBluetoothLeService.readCharacteristic(mChar);
                    } else {
                        Log.e(TAG, "Did not find char!");
                    }
                } else {
                    Log.e(TAG, "NOT CONNECTED");
                    restartBenchmark();
                }
            } else if (s.getBle_operation().equals("write_characteristic")) {
                Log.e(TAG, "write_characteristic");
                if (mBluetoothLeService != null && mConnected) {
                    String mUuid = s.getFilters().get(0); //FIXME just first element for now
                    if (allChars.containsKey(mUuid)) {
                        BluetoothGattCharacteristic mChar = allChars.get(mUuid);
                        byte[] bytes = new byte[20];
                        Arrays.fill(bytes, (byte) 1); //just fill with 1s
                        mChar.setValue(bytes);
                        long t_write_char = System.currentTimeMillis();
                        s.getPhone_step_result().addTimeWriteRequestStartGattResult(t_write_char);
                        mBluetoothLeService.writeCharacteristic(mChar);
                    }
                } else {
                    Log.e(TAG, "NOT CONNECTED");
                    restartBenchmark();
                }

            } else if (s.getBle_operation().equals("notification_characteristic")) {
                if (mBluetoothLeService != null && mConnected) {
                    String mUuid = s.getFilters().get(0); //FIXME just first element for now
                    if (allChars.containsKey(mUuid)) {
                        mBluetoothLeService.setCharacteristicNotification(allChars.get(mUuid), true);
                    }
                } else {
                    Log.e(TAG, "NOT CONNECTED");
                    restartBenchmark();
                }
            }
        } else {
            Log.e(TAG, "NOT IMPLEMENTED");
            Running = false;
        }
    }
    //gets called after we finish a step
    private void syncBenchmarkStatus(final Benchmark b) {
//        pool.shutdownNow();
//        pool = Executors.newSingleThreadExecutor();
        boolean wifiEnabled = wifiManager.isWifiEnabled();
        if (!wifiEnabled) {
            wifiManager.setWifiEnabled(true);
        }
        int activeStep = b.getActiveStep();
        if (b.getPhone().getSteps().size() > activeStep+1) {
            //another step is waiting
            Log.d(TAG, "Running next step");
            activeStep = activeStep + 1;
            b.setActiveStep(activeStep);
            Log.d(TAG, "step callback: " + b.getActiveStep());
            Running = false;
            scheduleNextStep(b);
        } else { //finished one benchmark
            b.getBenchmark_result().setStop_battery_level(getBatteryLevel());

            Uri alarmSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);

            Notification n  = new Notification.Builder(context)
                    .setContentTitle("STOP")
                    .setSmallIcon(android.R.drawable.arrow_up_float)
                    .setContentText(b.getName()).setPriority(Notification.PRIORITY_MAX).build(); //setSound(alarmSound).build();


            NotificationManager notificationManager =
                    (NotificationManager) getSystemService(NOTIFICATION_SERVICE);

            notificationManager.notify(0, n);

            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            notificationManager.notify(0, n);

            notificationManager.cancelAll();

            new Thread(new Runnable() {
                public void run() {
                    Log.e(TAG, "Finished one benchmark");
                    mLeDevices = new HashMap<String, BluetoothDevice>();
//            mBluetoothLeService.disconnect(); //disconnecting potentially open GATT (should be already closed...)
                    boolean postWorked = false;
                    for (int i = 0; i < 5;i++) {
                        postWorked = postBenchmarkResult(b);
                        if (postWorked) {
                            break;
                        }
                        try {
                            Thread.sleep(2000);
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                    }
                    if (postWorked) {
                        Log.d(TAG, "Posted result successfully");
                        try {
                            benchmarkQueue.removeFirst(); // remove succesfully run benchmark
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                        restartBenchmark();
                    } else {
                        Log.e(TAG, "Posted result NOT SUCCESSFUL");
                        Log.e(TAG, "Restarting same benchmark...");
                        restartBenchmark();
                    }
                }
            }).start();
        }
    }

    //either restart a failed benchmark or prepare the next one
    private void restartBenchmark() {
        Log.d(TAG, "Restarting Benchmark");
        pool.shutdownNow();
        pool = Executors.newSingleThreadExecutor();
        Benchmark b_run = benchmarkQueue.peekFirst();
        mBluetoothLeService.disconnect(); //disconnecting potentially open GATT (should be already closed...)
        mBluetoothLeService.close(); //disconnecting potentially open GATT (should be already closed...)
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        try {
            unregisterReceiver(mWifiBroadcastReceiver);
        } catch (Exception e) {
            Log.w(TAG, "mWifiBroadcastReceiver not registered, should not matter...");
        }
        try {
            unregisterReceiver(mGattBroadcastReceiver);
        } catch (Exception e) {
            Log.w(TAG, "mGattBroadcastReceiver not registered, should not matter...");
        }
        Running = false;
        if (b_run != null) {
            b_run.setActiveStep(0);
            b_run.resetAllBenchmarkReults();
            schedulePreBenchmark(b_run);

        } else {
            Log.e(TAG, "End of Queue");
            Log.e(TAG, "Finished all Benchmarks successfully :-)");

            Uri alarmSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);

            Notification n  = new Notification.Builder(context)
                    .setContentTitle("DONE")
                    .setSmallIcon(android.R.drawable.arrow_up_float)
                    .setContentText("DONE ALL").setPriority(Notification.PRIORITY_MAX).setSound(alarmSound).build();


            NotificationManager notificationManager =
                    (NotificationManager) getSystemService(NOTIFICATION_SERVICE);

            notificationManager.notify(2, n);



            stopBenchmark();
        }
    }

    private void stopBenchmark() {
        if (mWifiBroadcastReceiver != null) {
            try {
                unregisterReceiver(mWifiBroadcastReceiver);
            } catch (IllegalArgumentException e) {
                Log.w(TAG, "mWifiBroadcastReceiver not registered, should not matter...");
            }
        }
        // stop wifiactive here
        stopSelf();
    }


    private void scanLeDevice(final boolean enable, final List<ScanFilter> filters, final BluetoothLeScannerCompat scanner, ScanSettings settings, final MyBLEScanCallback callback, int scan_period) {

        if (enable) {
            // Stops scanning after a pre-defined scan period.
            BLEHandler.postDelayed(new Runnable() {
                @Override
                public void run() {
                    scanner.stopScan(callback);
                    Log.d(TAG, "Stopped benchmark step");
                    syncBenchmarkStatus(callback.benchmark);
                }
            }, scan_period);
            callback.benchmark.getPhone().getSteps().get(callback.benchmark.getActiveStep()).getPhone_step_result().setStartTime(System.currentTimeMillis());
            long t_now = System.currentTimeMillis();
            callback.stopTime= (scan_period+t_now);
            scanner.startScan(filters, settings, callback);
        } else {
            scanner.flushPendingScanResults(callback);
            scanner.stopScan(callback);
        }
    }


    // post the benchmark we want to run
    private boolean postBenchmark(Benchmark b) {
        while (!Util.isConnected(this)) {
            //Wait to connect
            try {
                wifiManager.setWifiEnabled(true);
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        // wait again because sometimes isConnected returns true even it's not...
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        Log.d(TAG, "DOING POST");
        String r = NetManager.getInstance().performPostCall(DataHolder.getInstance().BLEVA_SERVER + "/benchmark", b.getJsonOriginal());
        Log.d(TAG, "Response: " + r);
        if (r.equals("{\"result\":\"Success\"}")) {
            return true;
        } else {
            return false;
        }
    }

    // sync start of benchmark steps with dongles
    private boolean postBenchmarkSync(Benchmark b) {
        Log.d(TAG, "DOING SYNC");
        String r = NetManager.getInstance().performPostCall(DataHolder.getInstance().BLEVA_SERVER + "/benchmark/run", b.getJsonOriginal());
        Log.d(TAG, "Response: " + r);
        if (r.equals("{\"result\":\"Success\"}")) {
            return true;
        } else {
            return false;
        }
    }

    // post the benchmark result to server
    private boolean postBenchmarkResult(Benchmark b) {
        while (!Util.isConnected(this)) {
            //Wait to connect
            try {
                wifiManager.setWifiEnabled(true);
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        Log.d(TAG, "checking server availability another time...");
        int code = 0;
        while (code != 200) {
            URL url = null;
            try {
                url = new URL(DataHolder.getInstance().BLEVA_SERVER);
            } catch (MalformedURLException e) {
                e.printStackTrace();
            }
            HttpURLConnection connection = null;
            try {
                connection = (HttpURLConnection) url.openConnection();
            } catch (IOException e) {
                e.printStackTrace();
            }
            try {
                code = connection.getResponseCode();
            } catch (IOException e) {
                e.printStackTrace();
            }

            if (code == 200) {
                Log.d(TAG, "reachable");
            } else {
                Log.d(TAG, "not reachable");
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }

        Log.d(TAG, "DOING POST RESULTS");
        Gson gson = new Gson();
        String r = NetManager.getInstance().performPostCall(DataHolder.getInstance().BLEVA_SERVER + "/benchmark/result", gson.toJson(b)); //b.getJsonObject().toString());
        Log.d(TAG, "Response: " + r);
        if (r.equals("{\"result\":\"Success\"}")) {
            return true;
        } else {
            return false;
        }
    }


    private class MyBLEScanCallback extends no.nordicsemi.android.support.v18.scanner.ScanCallback {

        private static final String TAG = "MyBLEScanCallback";
        public Benchmark benchmark;
        public PhoneStep step;
        public BluetoothLeScannerCompat scanner;
        List<ScanFilter> filters;
        ScanSettings settings;
        public long stopTime;
        long currentTime;

        @Override
        public void onScanResult(int callbackType, ScanResult result) {
//            Log.d(TAG, result.toString());
//            if (!POWER_MEASUREMENT) {
                benchmark.getPhone().getSteps().get(benchmark.getActiveStep()).getPhone_step_result().addResult(result);
                mLeDevices.put(result.getDevice().getName(), result.getDevice());// TODO add to gatt
                currentTime = System.currentTimeMillis();
//            Log.d(TAG, "t: "+currentTime);
//                Notification n  = new Notification.Builder(context)
//                        .setContentTitle("Time Scan Result")
//                        .setSmallIcon(android.R.drawable.ic_lock_idle_charging)
//                        .setContentText(Long.toString(currentTime)).build();
//                NotificationManager notificationManager =
//                        (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
//                notificationManager.notify(2, n);


            // make sure that really we stop scanning after we have run out of time
            if (currentTime>=stopTime) {
                    scanner.stopScan(this);
                    Log.d(TAG, "Stopped scanning");
                    syncBenchmarkStatus(this.benchmark);
                }
//            }
//            if (rescanning) { //// TODO: 22/03/16 this was for doing rescanning benchmarks
//                scanner.stopScan(this);
//                scanner.startScan(filters, settings, this);
//            }
        }
        /**
         * Callback when batch results are delivered.
         *å
         * @param results List of scan results that are previously scanned.
         */
        @Override
        public void onBatchScanResults(List<ScanResult> results) {
//            Log.d(TAG, results.toString());
//            if (!POWER_MEASUREMENT) {

                benchmark.getPhone().getSteps().get(benchmark.getActiveStep()).getPhone_step_result().addResults(results);
//            }
        }

        /**
         * Callback when scan could not be started.
         *
         * @param errorCode Error code (one of SCAN_FAILED_*) for scan failure.
         */
        @Override
        public void onScanFailed(int errorCode) {
            Log.e(TAG, "onScanFailed: " + errorCode);
        }
    }

    private class AlarmReceiver extends BroadcastReceiver {

        @Override
        public void onReceive(Context c, Intent intent) {
            Log.i("AlarmReceiver", "Got alarm");
        }
    }

    private class WifiBroadcastReceiver extends BroadcastReceiver {
        private Benchmark b;
        private Boolean run =false;

        public WifiBroadcastReceiver(Benchmark b) {
            this.b = b;
        }
        @Override
        public void onReceive(Context c, Intent intent) {
            if (!run) {
                run = true;
                try {
                    unregisterReceiver(mWifiBroadcastReceiver);
                } catch (Exception e) {
                    Log.w(TAG, "mWifiBroadcastReceiver not registered, should not matter...");
                }
                wifiResults = wifiManager.getScanResults();
                b.getBenchmark_result().setWifi_results(wifiResults);
                Log.d(TAG, "WIFIRESULTS " + wifiResults.toString());
                scheduleNextBenchmark(b);
            }
        }
    }

    // Handles various events fired by the Service.
    // ACTION_GATT_CONNECTED: connected to a GATT server.
    // ACTION_GATT_DISCONNECTED: disconnected from a GATT server.
    // ACTION_GATT_SERVICES_DISCOVERED: discovered GATT services.
    // ACTION_DATA_AVAILABLE: received data from the device.  This can be a result of read
    //                        or notification operations.
    private class GattBroadcastReceiver extends BroadcastReceiver {

        private Benchmark b;

        public GattBroadcastReceiver(Benchmark b) {
            this.b = b;
        }

        @Override
        public void onReceive(Context context, Intent intent) {
            final String action = intent.getAction();
            int activeStep = b.getActiveStep();
            String ble_op = b.getPhone().getSteps().get(b.getActiveStep()).getBle_operation();
            PhoneStep phoneStep = b.getPhone().getSteps().get(b.getActiveStep());
            Log.d(TAG, "ACTION: " + action);
            if (BluetoothLeService.ACTION_GATT_CONNECTED.equals(action)) {
                long t_connect = System.currentTimeMillis();
                Log.d(TAG, "ACTION_GATT_CONNECTED");
                mConnected = true;
                phoneStep.getPhone_step_result().addTimeConnectedGattResult(t_connect);
                // we are already finished
                if (ble_op.equals("connecting")) {
                    Log.d(TAG, "Stopped connecting step");
                    if(b.lastStep()) {
                        mBluetoothLeService.disconnect();
                    } else {
                        syncBenchmarkStatus(b);
                    }
                }
            } else if (BluetoothLeService.ACTION_GATT_DISCONNECTED.equals(action)) {
                mConnected = false;
                long t_disconnect = System.currentTimeMillis();
                phoneStep.getPhone_step_result().addTimeDisconnectedGattResult(t_disconnect);
                Log.d(TAG, "ACTION_GATT_DISCONNECTED");
                syncBenchmarkStatus(b);
            } else if (BluetoothLeService.ACTION_GATT_SERVICES_DISCOVERED.equals(action)) {
                long t_gatt_services = System.currentTimeMillis();
                Log.d(TAG, "ACTION_GATT_SERVICES_DISCOVERED");
                List<BluetoothGattService> gattServices = mBluetoothLeService.getSupportedGattServices();
                Log.d(TAG, "services and characteristics: " + gattServices.toString());
                for (BluetoothGattService gattService : gattServices) {
                    List<BluetoothGattCharacteristic> gattCharacteristics =
                            gattService.getCharacteristics();
                    allChars = new HashMap<String, BluetoothGattCharacteristic>();
                    for (BluetoothGattCharacteristic gattCharacteristic : gattCharacteristics) {
                        String uuid = gattCharacteristic.getUuid().toString();
                        allChars.put(uuid, gattCharacteristic);
                    }
                }
                phoneStep.getPhone_step_result().addTimeServicesDiscoverdGattResult(t_gatt_services);
                if (ble_op.equals("service_discovery")) {
                    Log.d(TAG, "Stopped service_discovery step");
                    if(b.lastStep()) {
                        mBluetoothLeService.disconnect();
                    } else {
                        syncBenchmarkStatus(b);
                    }
                }
            } else if (BluetoothLeService.ACTION_DATA_AVAILABLE.equals(action)) {
                long t_read_char = System.currentTimeMillis();
                Log.d(TAG, "ACTION_DATA_AVAILABLE");
                final String char_data = intent.getStringExtra(BluetoothLeService.EXTRA_DATA);
                Log.d(TAG, "getDataString"+char_data);
                if (ble_op.equals("read_characteristic")) {
                    phoneStep.getPhone_step_result().addTimeReadRequestDoneGattResult(t_read_char);
                    Log.d(TAG, "Stopped read_characteristic step");
                    if(b.lastStep()) {
                        mBluetoothLeService.disconnect();
                    } else {
                        syncBenchmarkStatus(b);
                    }
                } else if (ble_op.equals("notify_characteristic")){
                    Log.d(TAG, "notification");
                    if(b.lastStep()) {
                        mBluetoothLeService.disconnect();
                    } else {
                        syncBenchmarkStatus(b);
                    }
                }
            } else if (BluetoothLeService.ACTION_WRITE_COMPLETED.equals(action)) {
                long t_write_char = System.currentTimeMillis();
                Log.d(TAG, "ACTION_WRITE_COMPLETED");
                if (ble_op.equals("write_characteristic")) {
                    phoneStep.getPhone_step_result().addTimeWriteRequestDoneGattResult(t_write_char);
                    Log.d(TAG, "Stopped read_characteristic step");
                    if(b.lastStep()) {
                        mBluetoothLeService.disconnect();
                    } else {
                        syncBenchmarkStatus(b);
                    }
                }
            }
        }
    }

    private class WifiActiveService implements Runnable {
        private Handler mHandler;
        private Benchmark b;
        private long runTime;
        private long startTime = System.currentTimeMillis();
        public WifiActiveService(Benchmark b){
            this.b = b;
            this.runTime = (long) b.getTime();
            this.mHandler = new Handler(Looper.getMainLooper()){
                @Override
                public void handleMessage(Message inputMessage){
                    String msg = (String) inputMessage.obj;
                    Toast.makeText(getApplicationContext(), "" + msg, Toast.LENGTH_SHORT).show();
                }
            };
        }
        @Override
        public void run() {
            sendMessage(1, "simulating wifi traffic...");
            ArrayList<String> hosts = new ArrayList<String>();
            hosts.add("http://130.226.142.195/bigdata/10MB.zip");
            while ((System.currentTimeMillis() - startTime < (runTime-3000))) {
                for (String s : hosts) {
                    boolean reachable;
                    long t0 = System.currentTimeMillis();
                    long t1;
                    try {
                        reachable =  InetAddress.getByName("130.226.142.195").isReachable(3000);
                        t1 = System.currentTimeMillis();
                    } catch (IOException e) {
                        e.printStackTrace();
                        reachable = false;
                        t1 = System.currentTimeMillis();
                    }
                    WifiResult wifi_result = NetManager.getInstance().performGetCall(s);
                    wifi_result.setLatency(t1-t0);
                    b.getPhone().getSteps().get(b.getActiveStep()).getPhone_step_result().addWiFiResult(wifi_result);
                }
            }
        }

        public void sendMessage(int what, String msg){
            Message message = mHandler.obtainMessage(what , msg);
            message.sendToTarget();
        }
    }

    private static IntentFilter makeGattUpdateIntentFilter() {
        final IntentFilter intentFilter = new IntentFilter();
        intentFilter.addAction(BluetoothLeService.ACTION_GATT_CONNECTED);
        intentFilter.addAction(BluetoothLeService.ACTION_GATT_DISCONNECTED);
        intentFilter.addAction(BluetoothLeService.ACTION_GATT_SERVICES_DISCOVERED);
        intentFilter.addAction(BluetoothLeService.ACTION_DATA_AVAILABLE);
        intentFilter.addAction(BluetoothLeService.ACTION_WRITE_COMPLETED);
        return intentFilter;
    }

    public float getBatteryLevel() {
        Intent batteryIntent = registerReceiver(null, new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
        int level = batteryIntent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1);
        int scale = batteryIntent.getIntExtra(BatteryManager.EXTRA_SCALE, -1);
        Log.d(TAG, "Battery level "+((float)level / (float)scale)) ;
        return ((float)level / (float)scale);
    }
}

