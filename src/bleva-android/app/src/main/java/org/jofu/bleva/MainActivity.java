package org.jofu.bleva;
import android.Manifest;
import android.app.Activity;
import android.app.ActivityManager;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.provider.ContactsContract;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.text.InputType;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.EditText;
import android.widget.ListView;

import java.net.NetworkInterface;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.List;

public class MainActivity extends AppCompatActivity {

    private final static String TAG = "MainActivity";
    private ArrayList<Benchmark> Benchmarks;

    public Deque<Benchmark> benchmarkQueue; // the benchmarks we schedule to run

    //service
    private Intent benchmarkServiceIntent;

    //wifi
    private WifiManager wifiManager;

    private String m_Text = "";

    @Override
    protected void onCreate(Bundle savedInstanceState){
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // make sure wifi is on
        wifiManager = (WifiManager) this.getSystemService(Context.WIFI_SERVICE);
        boolean wifiEnabled = wifiManager.isWifiEnabled();
        if (!wifiEnabled) {
            wifiManager.setWifiEnabled(true);
        }
        // resetting BLE adapter to begin
        Util.resetBluetoothAdapter();

        //TODO this is kind of buggy because a new activity is started before this message is displayed
        showPermissionDialog();

        benchmarkServiceIntent = new Intent(this, BenchmarkService.class);


        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        // Run bechmarks button
        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(final View view) {
                Snackbar.make(view, "Starting Benchmarks", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
//                startService(benchmarkServiceIntent);
//
                benchmarkQueue = new ArrayDeque<Benchmark>();
                ArrayList <Benchmark> benchmarks = DataHolder.getInstance().getSelectedBenchmarks();
                Log.d(TAG, benchmarks.toString());
                for (Benchmark b : benchmarks) {
                    int repetitions = b.getRepetitions();
                    for (int i = 0; i < repetitions;i++) {
                        benchmarkQueue.add(b);
                        Log.d(TAG, "Added: "+b.getName());
                    }
                }
                DataHolder.getInstance().setBenchmarkQueue(benchmarkQueue);
                if (isMyServiceRunning(BenchmarkService.class)) {
                    try {
                        stopService(benchmarkServiceIntent);

                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
                startService(benchmarkServiceIntent);
            }
        });

        Benchmarks = DataHolder.getInstance().getBenchmarks();
        if (Benchmarks.isEmpty()) {
            Benchmarks = new ArrayList<Benchmark>();
            NetManager.getInstance().GETStringRequest(DataHolder.getInstance().BLEVA_SERVER + "/benchmarks", new GETListener<String>() {
                @Override
                public void onSuccess(String result) {
                    Benchmarks = Util.decodeJSONBenchmarks(result);
                    Log.d(TAG, Benchmarks.toString());
                    DataHolder.getInstance().setBenchmarks(Benchmarks);
                    finish();
                    startActivity(getIntent());
                }

                public void onFail(Exception e) {
                    Log.e(TAG, e.toString());
                }
            });
        }

        // Create the adapter to convert the array to views
        BenchmarkAdapter adapter = new BenchmarkAdapter(this, DataHolder.getInstance().getBenchmarks());
        // Attach the adapter to a ListView
        ListView listView = (ListView) findViewById(R.id.list);
        listView.setAdapter(adapter);
//        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
//            @Override
//            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
//                Log.d(TAG, "Clicked Benchmark ");
//                //The position where the list item is clicked is obtained from the
//                //the parameter position of the android listview
//                String itemDesc = DataHolder.getInstance().getBenchmarks().get(position).toString();
//
//                //In order to start displaying new activity we need an intent
//                Intent intent = new Intent(getApplicationContext(), BenchmarkActivity.class);
//                intent.putExtra("itemDesc", itemDesc);
//
//                //Here we will pass the previously created intent as parameter
//                startActivity(intent);
//            }
//        });

//        listView.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
//            @Override
//            public void onItemSelected(AdapterView<?> arg0,
//                                       View arg1, int arg2, long arg3) {
//                Log.d(TAG, "Selected Benchmark");
//
//            }
//            @Override
//            public void onNothingSelected(AdapterView<?> arg0) {
//                Log.d(TAG, "Nothing Selected");
//            }
//        });
        String macA = getMacAddr();
        DataHolder.getInstance().setMacAddress(macA);
    }

    public static String getMacAddr() {
        try {
            List<NetworkInterface> all = Collections.list(NetworkInterface.getNetworkInterfaces());
            for (NetworkInterface nif : all) {
                if (!nif.getName().equalsIgnoreCase("wlan0")) continue;

                byte[] macBytes = nif.getHardwareAddress();
                if (macBytes == null) {
                    return "";
                }

                StringBuilder res1 = new StringBuilder();
                for (byte b : macBytes) {
                    res1.append(Integer.toHexString(b & 0xFF) + ":");
                }

                if (res1.length() > 0) {
                    res1.deleteCharAt(res1.length() - 1);
                }
                return res1.toString();
            }
        } catch (Exception ex) {
        }
        return "02:00:00:00:00:00";
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_scan) {
            AlertDialog.Builder builder = new AlertDialog.Builder(this);
            builder.setTitle("No. of Phones");

            // Set up the input
            final EditText input = new EditText(this);
            // Specify the type of input expected; this, for example, sets the input as a password, and will mask the text
            input.setInputType(InputType.TYPE_CLASS_NUMBER);
            builder.setView(input);

            // Set up the buttons
            builder.setPositiveButton("OK", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    m_Text = input.getText().toString();
                    int no_Phones = Integer.parseInt(m_Text);
                    for (Benchmark b : DataHolder.getInstance().getBenchmarks()) {
                        b.getPhone().setReplicas(no_Phones);
                        b.setJsonOriginal(b.toString());
                    }
                }
            });
            builder.setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    dialog.cancel();
                }
            });

            builder.show();

            return true;
        } else if  (id ==R.id.action_select_all) {
            Log.d(TAG, "Select all");
            for (Benchmark b : DataHolder.getInstance().getBenchmarks()) {
                b.setSelected(true);
            }
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    @Override
    protected void onResume() {
        super.onResume();
    }

    @Override
    protected void onPause() {
        super.onPause();
    }


    @Override
    protected void onStop() {
        super.onStop();  // Always call the superclass method first
        boolean wifiEnabled = wifiManager.isWifiEnabled();
        if (!wifiEnabled) {
            wifiManager.setWifiEnabled(true);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();  // Always call the superclass method first
        boolean wifiEnabled = wifiManager.isWifiEnabled();
        if (!wifiEnabled) {
            wifiManager.setWifiEnabled(true);
        }
    }
    private void showPermissionDialog() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(
                    this,
                    new String[]{Manifest.permission.ACCESS_COARSE_LOCATION, Manifest.permission.ACCESS_FINE_LOCATION},
                    DataHolder.MY_PERMISSIONS_REQUEST_ACCESS_FINE_LOCATION);

        } else {
            Log.i(TAG, "Location Permission already granted");
        }
   }

    @Override
    public void onRequestPermissionsResult(int requestCode,
                                           String permissions[], int[] grantResults) {
        switch (requestCode) {
            case DataHolder.MY_PERMISSIONS_REQUEST_ACCESS_FINE_LOCATION: {
                // If request is cancelled, the result arrays are empty.
                if (grantResults.length > 0
                        && grantResults[0] == PackageManager.PERMISSION_GRANTED) {

                } else {
//                    finish();

                    return;
                }
                return;
            }

            // other 'case' lines to check for other
            // permissions this app might request
        }
    }


    private boolean isMyServiceRunning(Class<?> serviceClass) {
        ActivityManager manager = (ActivityManager) getSystemService(Context.ACTIVITY_SERVICE);
        for (ActivityManager.RunningServiceInfo service : manager.getRunningServices(Integer.MAX_VALUE)) {
            if (serviceClass.getName().equals(service.service.getClassName())) {
                return true;
            }
        }
        return false;
    }

}