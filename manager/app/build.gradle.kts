plugins {
    id("com.android.application")
}

android {
    namespace = "pt.vcaitano.vocmanager"
    compileSdk = 36

    defaultConfig {
        applicationId = "pt.vcaitano.vocmanager"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "1.0.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
