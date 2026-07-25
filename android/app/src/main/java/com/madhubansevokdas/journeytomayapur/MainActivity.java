package com.madhubansevokdas.journeytomayapur;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(DebugInfoPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
