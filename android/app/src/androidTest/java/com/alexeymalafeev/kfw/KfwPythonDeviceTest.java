package com.alexeymalafeev.kfw;

import android.content.Context;

import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;

import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import org.json.JSONObject;
import org.junit.Test;
import org.junit.runner.RunWith;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

@RunWith(AndroidJUnit4.class)
public class KfwPythonDeviceTest {
    @Test
    public void completePythonRuntimeOnDevice() throws Exception {
        Context context = InstrumentationRegistry.getInstrumentation().getTargetContext();
        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(context));
        }
        String result = Python.getInstance()
                .getModule("kfw_android_selftest")
                .callAttr("run_suite", context.getFilesDir().getAbsolutePath())
                .toString();
        JSONObject report = new JSONObject(result);
        assertEquals("passed", report.getString("status"));
        assertTrue(report.getInt("fighters") > 50);
        assertTrue(report.getInt("fight_menus") > 0);
        assertTrue(report.getBoolean("russian"));
    }
}
