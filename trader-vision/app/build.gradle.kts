plugins { id("com.android.application") }

android {
    namespace = "pt.vcaitano.tradervision"
    compileSdk = 36
    defaultConfig {
        applicationId = "pt.vcaitano.tradervision"
        minSdk = 29
        targetSdk = 35
        versionCode = 1
        versionName = "0.1.0-demo"
    }
    buildTypes {
        getByName("release") { isMinifyEnabled = false }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
