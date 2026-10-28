plugins {
    id("com.android.application")
    id("com.chaquo.python")
}

android {
    namespace = "com.alexeymalafeev.kfw"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.alexeymalafeev.kfw"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        ndk {
            abiFilters += setOf("arm64-v8a", "x86_64")
        }
    }

    buildTypes {
        getByName("debug") {
            versionNameSuffix = "-debug"
        }
        getByName("release") {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    sourceSets {
        getByName("main") {
            assets.srcDir("$buildDir/generated/assets/main")
        }
    }

    lint {
        abortOnError = true
    }

    bundle {
        language {
            enableSplit = false
        }
    }
}

chaquopy {
    defaultConfig {
        version = "3.13"
        pyc {
            src = false
        }
    }
    sourceSets {
        getByName("main") {
            srcDir("$buildDir/generated/python/main")
        }
        getByName("debug") {
            srcDir("$buildDir/generated/python/debug")
        }
    }
}

val repositoryRoot = rootDir.parentFile

val syncPythonMain by tasks.registering(Sync::class) {
    from("$repositoryRoot/kf_lib") {
        into("kf_lib")
        include("**/*.py")
        exclude("**/__pycache__/**")
    }
    from(repositoryRoot) {
        include("moves/*.txt")
        include("quotes/*.txt")
        include("quotes/ru/*.txt")
        include("locale/ru/LC_MESSAGES/*.mo")
    }
    from("$rootDir/python") {
        include("*.py")
    }
    into("$buildDir/generated/python/main")
}

val syncPythonDebug by tasks.registering(Sync::class) {
    from("$rootDir/python_debug") {
        include("*.py")
    }
    into("$buildDir/generated/python/debug")
}

val syncAssetsMain by tasks.registering(Sync::class) {
    from(repositoryRoot) {
        include("LICENSE")
        rename("LICENSE", "LICENSE.txt")
    }
    into("$buildDir/generated/assets/main")
}

tasks.named("preBuild") {
    dependsOn(syncPythonMain, syncPythonDebug, syncAssetsMain)
}
tasks.configureEach {
    when (name) {
        "mergeDebugPythonSources" -> dependsOn(syncPythonMain, syncPythonDebug)
        "mergeReleasePythonSources" -> dependsOn(syncPythonMain)
        "mergeDebugAssets", "mergeReleaseAssets" -> dependsOn(syncAssetsMain)
    }
}

dependencies {
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20240303")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test:runner:1.6.2")
}
