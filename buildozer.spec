[app]
title = My App
package.name = myapp
package.domain = org.example
source.dir = .
version = 1.0

requirements = python3==3.9, kivy, cython==0.29.36, libffi==3.4.4
orientation = portrait
fullscreen = 0

android.api = 31
android.minapi = 21

android.ndk = 28.2.10981533
android.ndk_api = 21
android.archs = arm64-v8a
android.use_precompiled = True
android.precompiled_dir = ./precompiled

android.enable_androidx = True
android.enable_jetifier = True

android.extra_cflags = -O2 -fPIC -DNDEBUG
android.extra_ldflags = -Wl,-z,max-page-size=16384,-z,common-page-size=16384

source.include_exts = py,png,jpg,kv,ttf,otf,json,xml,ttc,woff,woff2
source.include_dirs = fonts,images,data,assets

android.manifest = <?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="org.example.myapp"
    android:versionCode="1"
    android:versionName="1.0">
    
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    
    <uses-feature android:name="android.hardware.touchscreen" android:required="false" />
    
    <application
        android:allowBackup="true"
        android:icon="@drawable/icon"
        android:label="My App"
        android:theme="@style/AppTheme"
        android:exported="false">
        
        <activity
            android:name="org.kivy.android.PythonActivity"
            android:configChanges="orientation|keyboardHidden|screenSize|screenLayout|uiMode"
            android:label="My App"
            android:launchMode="singleTask"
            android:exported="true">
            
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>

log_level = 2

android.accept_sdk_license = True

[buildozer]
