package org.jofu.bleva;

import android.app.Application;
import android.content.Context;

public class BLEva extends Application {
    private static Context mContext;

    public void onCreate() {
        super.onCreate();

        // Initialize the singletons so their instances
        // are bound to the application process.
        initSingletons();
    }

    protected void initSingletons() {
        DataHolder.initInstance();
        // Initialize the instance of NetManager
        NetManager.initInstance(this);
    }
}