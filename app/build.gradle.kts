plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.hmsproject"
    compileSdk = 33

    defaultConfig {
        applicationId = "com.example.hmsproject"
        minSdk = 30
        targetSdk = 33
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
    buildFeatures {
        viewBinding = true
    }
}

dependencies {

    implementation("androidx.core:core-ktx:1.9.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.8.0")

    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")

    implementation("com.baidu.lbsyun:BaiduMapSDK_Map:7.4.0")
    implementation("com.baidu.lbsyun:BaiduMapSDK_Search:7.4.0")
    implementation("com.baidu.lbsyun:BaiduMapSDK_Util:7.4.0")
    implementation("com.baidu.lbsyun:BaiduMapSDK_Location:9.3.7")

    implementation ("org.eclipse.paho:org.eclipse.paho.client.mqttv3:1.2.5")
    implementation ("org.eclipse.paho:org.eclipse.paho.android.service:1.1.1")
    implementation ("io.github.youth5201314:banner:2.2.2")
    implementation ("com.github.bumptech.glide:glide:4.11.0")
    implementation ("org.jetbrains.kotlinx:kotlinx-serialization-json:1.3.3")

}