[app]
# ==================== 基础信息 ====================
title = 我的应用
package.name = myapp
package.domain = org.example
source.dir = .
version = 1.0

# ==================== 依赖配置 ====================
requirements = python3==3.9.18, kivy, cython==0.29.36  
orientation = portrait
fullscreen = 0

# ==================== Android 版本配置 ====================
# 使用您指定的 NDK r28c 和 API 31
android.api = 31
android.minapi = 21
android.ndk = 28c
android.ndk_api = 21
android.sdk = 31
android.arch = arm64-v8a

# ==================== 高级优化配置 ====================
# 1. AndroidX 支持（现代架构）
android.enable_androidx = True
android.enable_jetifier = True

# 2. 性能优化编译标志
android.extra_cflags = -O2 -fPIC -DNDEBUG

# 3. 16K 内存对齐（关键性能优化）
android.extra_ldflags = -Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384

# 4. 包含所有文件类型
source.include_exts = py,png,jpg,kv,ttf,otf,json,xml,ttc,woff,woff2

# 5. 包含资源目录（根据实际情况调整）
source.include_dirs = fonts, images, data, assets

# ==================== API 31 强制配置 ====================
# 6. Android Manifest 配置（满足 API 31 要求）
android.manifest = <?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="org.example.myapp"
    android:versionCode="1"
    android:versionName="1.0">
    
    <!-- 权限声明 -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    
    <!-- 设备特性声明 -->
    <uses-feature android:name="android.hardware.touchscreen" android:required="false" />
    
    <application
        android:allowBackup="true"
        android:icon="@drawable/icon"
        android:label="我的应用"
        android:theme="@style/AppTheme"
        android:exported="false">
        
        <!-- 主Activity（必须显式声明exported） -->
        <activity
            android:name="org.kivy.android.PythonActivity"
            android:configChanges="orientation|keyboardHidden|screenSize|screenLayout|uiMode"
            android:label="我的应用"
            android:launchMode="singleTask"
            android:exported="true">
            
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        
        <!-- 其他组件（按需添加） -->
    </application>
</manifest>

# ==================== 其他优化 ====================
# 7. 日志级别
log_level = 2

# 8. 构建优化
android.accept_sdk_license = True

[buildozer]
