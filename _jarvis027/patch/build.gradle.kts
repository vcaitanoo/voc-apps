plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "pt.vcaitano.jarvis"
    compileSdk = 37

    defaultConfig {
        applicationId = "pt.vcaitano.jarvis"
        minSdk = 26
        targetSdk = 37
        versionCode = 9
        versionName = "0.2.7"

        buildConfigField(
            "String",
            "BRAIN_BASE_URL",
            "\"${project.findProperty("JARVIS_BRAIN_BASE_URL") ?: "https://khinnoxpesnhtmmvrken.supabase.co/functions/v1/jarvis-gateway"}\""
        )
        buildConfigField(
            "String",
            "SUPABASE_URL",
            "\"https://khinnoxpesnhtmmvrken.supabase.co\""
        )
        buildConfigField(
            "String",
            "SUPABASE_PUBLISHABLE_KEY",
            "\"sb_publishable_7te5SMQiAQ5ep2qi2Q4SbA_1_Mi4wAt\""
        )
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlin {
        jvmToolchain(17)
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
}

dependencies {
    implementation("androidx.core:core-ktx:1.18.0")
    implementation("androidx.activity:activity-compose:1.13.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.10.0")
    implementation("androidx.work:work-runtime-ktx:2.11.2")

    implementation("androidx.compose.ui:ui:1.12.0")
    implementation("androidx.compose.ui:ui-tooling-preview:1.12.0")
    implementation("androidx.compose.foundation:foundation:1.12.0")
    implementation("androidx.compose.material3:material3:1.4.0")

    debugImplementation("androidx.compose.ui:ui-tooling:1.12.0")
}
