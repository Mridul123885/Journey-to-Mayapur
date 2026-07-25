package com.madhubansevokdas.journeytomayapur;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * Exposes the real build type to the web layer so debug-only UI (test
 * menus, logs, developer options) can be shown in debug builds and
 * automatically hidden in the Play Store release build.
 *
 * BuildConfig.DEBUG is set by the Android Gradle Plugin itself based on
 * the build variant being assembled (assembleDebug vs assembleRelease /
 * bundleRelease) — it is not something the app can accidentally leave on,
 * since it's compiled in per-variant, not read from a runtime setting.
 */
@CapacitorPlugin(name = "DebugInfo")
public class DebugInfoPlugin extends Plugin {

    @PluginMethod
    public void isDebugBuild(PluginCall call) {
        JSObject ret = new JSObject();
        ret.put("isDebug", BuildConfig.DEBUG);
        call.resolve(ret);
    }
}
