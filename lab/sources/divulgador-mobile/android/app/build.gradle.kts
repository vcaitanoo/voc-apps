plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "pt.vcaitano.divulgador"
    compileSdk = 34

    defaultConfig {
        applicationId = "pt.vcaitano.divulgadormobile"
        minSdk = 24
        targetSdk = 34
        versionCode = (System.getenv("DIVULGADOR_VERSION_CODE") ?: "7").toInt()
        versionName = System.getenv("DIVULGADOR_VERSION_NAME") ?: "0.1.6"
    }

    signingConfigs {
        create("release") {
            val ksPath = System.getenv("DIVULGADOR_KEYSTORE_PATH")
            if (ksPath != null) {
                storeFile = file(ksPath)
                storePassword = System.getenv("DIVULGADOR_KEYSTORE_PASSWORD")
                keyAlias = System.getenv("DIVULGADOR_KEY_ALIAS")
                keyPassword = System.getenv("DIVULGADOR_KEY_PASSWORD") ?: System.getenv("DIVULGADOR_KEYSTORE_PASSWORD")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            signingConfig = signingConfigs.getByName("release")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { compose = true }
    composeOptions { kotlinCompilerExtensionVersion = "1.5.14" }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.4")
    implementation("androidx.activity:activity-compose:1.9.1")
    implementation(platform("androidx.compose:compose-bom:2024.06.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    // SMTP TLS com várias contas e fila agendada; sem abrir o Gmail por destinatário.
    implementation("androidx.work:work-runtime:2.9.1")
    implementation("com.sun.mail:android-mail:1.6.7")
    implementation("com.sun.mail:android-activation:1.6.7")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")
}
