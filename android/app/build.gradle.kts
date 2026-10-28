plugins {
    id("com.android.application")
    id("com.chaquo.python")
}

// The app version comes from the latest release tag (vX.Y.Z-beta), like the
// desktop game, which has no version string in code. Between releases git
// describe adds "-N-g<hash>", and "-dirty" for uncommitted changes. Without
// git or tags (e.g. a source zip) the build falls back to 0.0.0-dev.
val gitDescribe: String = runCatching {
    providers.exec {
        commandLine("git", "describe", "--tags", "--match", "v[0-9]*", "--dirty")
        workingDir = rootDir
        isIgnoreExitValue = true
    }.standardOutput.asText.get().trim()
}.getOrDefault("")
val appVersionName = gitDescribe.removePrefix("v").ifEmpty { "0.0.0-dev" }
// X.Y.Z -> X*10000 + Y*100 + Z: grows with every release, so Android accepts
// each new APK as an update.
val appVersionCode = Regex("""^(\d+)\.(\d+)\.(\d+)""").find(appVersionName)
    ?.destructured?.let { (x, y, z) -> x.toInt() * 10000 + y.toInt() * 100 + z.toInt() }
    ?.coerceAtLeast(1) ?: 1

android {
    namespace = "com.alexeymalafeev.kfw"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.alexeymalafeev.kfw"
        minSdk = 24
        targetSdk = 35
        versionCode = appVersionCode
        versionName = appVersionName
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
    // music and sound effects, rendered by dev_scripts/audio/render.py --game
    from(repositoryRoot) {
        include("audio/music/*.ogg")
        include("audio/sfx/*.ogg")
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
