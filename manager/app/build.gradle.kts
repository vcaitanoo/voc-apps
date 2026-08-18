plugins {
    id("com.android.application")
}

val releaseKeystorePath = providers.environmentVariable("VOC_MANAGER_KEYSTORE_PATH").orNull
val releaseStorePassword = providers.environmentVariable("VOC_MANAGER_STORE_PASSWORD").orNull
val releaseKeyAlias = providers.environmentVariable("VOC_MANAGER_KEY_ALIAS").orNull
val releaseKeyPassword = providers.environmentVariable("VOC_MANAGER_KEY_PASSWORD").orNull
val hasReleaseSigning = listOf(
    releaseKeystorePath,
    releaseStorePassword,
    releaseKeyAlias,
    releaseKeyPassword
).all { !it.isNullOrBlank() }

android {
    namespace = "pt.vcaitano.vocmanager"
    compileSdk = 36

    defaultConfig {
        applicationId = "pt.vcaitano.vocmanager"
        minSdk = 28
        targetSdk = 36
        versionCode = 5
        versionName = "1.2.1"
    }

    signingConfigs {
        if (hasReleaseSigning) {
            create("vocRelease") {
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
            if (hasReleaseSigning) {
                signingConfig = signingConfigs.getByName("vocRelease")
            }
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
