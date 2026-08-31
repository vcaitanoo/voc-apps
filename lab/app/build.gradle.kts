plugins {
    id("com.android.application")
}

val releaseKeystorePath = providers.environmentVariable("VOC_LAB_KEYSTORE_PATH").orNull
val releaseStorePassword = providers.environmentVariable("VOC_LAB_STORE_PASSWORD").orNull
val releaseKeyAlias = providers.environmentVariable("VOC_LAB_KEY_ALIAS").orNull
val releaseKeyPassword = providers.environmentVariable("VOC_LAB_KEY_PASSWORD").orNull
val hasReleaseSigning = listOf(releaseKeystorePath, releaseStorePassword, releaseKeyAlias, releaseKeyPassword).all { !it.isNullOrBlank() }

android {
    namespace = "pt.vcaitano.voclab"
    compileSdk = 36

    defaultConfig {
        applicationId = "pt.vcaitano.voclab"
        minSdk = 28
        targetSdk = 36
        versionCode = 3
        versionName = "1.0.2"
    }

    signingConfigs {
        if (hasReleaseSigning) {
            create("vocLabRelease") {
                storeFile = file(releaseKeystorePath!!)
                storePassword = releaseStorePassword
                keyAlias = releaseKeyAlias
                keyPassword = releaseKeyPassword
                enableV1Signing = true
                enableV2Signing = true
                enableV3Signing = true
                enableV4Signing = true
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            if (hasReleaseSigning) signingConfig = signingConfigs.getByName("vocLabRelease")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
