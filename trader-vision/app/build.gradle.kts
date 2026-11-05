plugins { id("com.android.application") }

android {
    namespace = "pt.vcaitano.tradervision"
    compileSdk = 36
    defaultConfig {
        applicationId = "pt.vcaitano.tradervision.gestaoteste"
        minSdk = 29
        targetSdk = 35
        versionCode = 6
        versionName = "0.6.0-demo"
    }
    // A identidade de assinatura é imutável após esta migração.
    // A keystore nunca é commitada; só é carregada durante o build autorizado.
    val permanentKeyFile = System.getenv("VOC_TRADER_KEYSTORE_FILE")
    signingConfigs {
        if (!permanentKeyFile.isNullOrBlank()) {
            create("vocTraderPermanent") {
                storeFile = file(permanentKeyFile)
                storePassword = System.getenv("VOC_TRADER_STORE_PASS")
                keyAlias = "voc-trader-release"
                keyPassword = System.getenv("VOC_TRADER_KEY_PASS")
            }
        }
    }
    buildTypes {
        getByName("release") {
            isMinifyEnabled = false
            if (!permanentKeyFile.isNullOrBlank()) {
                signingConfig = signingConfigs.getByName("vocTraderPermanent")
            }
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

// On-device, bundled Latin text recognizer. No screen image is uploaded.
dependencies {
    implementation("com.google.mlkit:text-recognition:16.0.1")
}
