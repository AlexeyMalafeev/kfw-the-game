package com.alexeymalafeev.kfw;

import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.AssetFileDescriptor;
import android.media.AudioAttributes;
import android.media.MediaPlayer;
import android.media.SoundPool;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.util.Log;

import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Music and sound effects, from the OGG files in assets/audio/ (rendered by
 * dev_scripts/audio/render.py --game). Music: a tune's intro file plays once and
 * hands over gaplessly to its loop file, which repeats. Effects: a SoundPool,
 * with bursts spaced out so the effects of one blow stay distinguishable.
 * All methods run on the main thread.
 */
final class GameAudio {
    private static final String TAG = "KFW";
    static final String MUSIC_ON = "music_on";
    static final String EFFECTS_ON = "effects_on";
    static final String TITLE_TUNE = "01_path_of_the_fist";
    private static final float MUSIC_VOLUME = 0.8f;
    // effects of one game event arrive together; start them this far apart,
    // and drop effects that would start later than the limit
    private static final long EFFECT_GAP_MS = 110;
    private static final long EFFECT_MAX_DELAY_MS = 1200;

    private final Context context;
    private final SharedPreferences preferences;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final SoundPool pool;
    private final Map<String, Integer> effectIds = new HashMap<>();
    private final Set<Integer> loadedEffects = new HashSet<>();
    private boolean musicOn;
    private boolean effectsOn;
    private boolean inForeground = true;
    private String tune;  // the wanted tune, also while muted or in the background
    private MediaPlayer intro;
    private MediaPlayer loop;
    private long nextEffectAt;

    GameAudio(Context context, SharedPreferences preferences) {
        this.context = context;
        this.preferences = preferences;
        musicOn = preferences.getBoolean(MUSIC_ON, true);
        effectsOn = preferences.getBoolean(EFFECTS_ON, true);
        pool = new SoundPool.Builder()
                .setMaxStreams(6)
                .setAudioAttributes(new AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_GAME)
                        .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                        .build())
                .build();
        pool.setOnLoadCompleteListener((soundPool, id, status) -> {
            if (status == 0) {
                loadedEffects.add(id);
            }
        });
        try {
            String[] files = context.getAssets().list("audio/sfx");
            if (files != null) {
                for (String file : files) {
                    if (file.endsWith(".ogg")) {
                        try (AssetFileDescriptor fd = context.getAssets().openFd("audio/sfx/" + file)) {
                            effectIds.put(file.substring(0, file.length() - 4), pool.load(fd, 1));
                        }
                    }
                }
            }
        } catch (IOException error) {
            Log.w(TAG, "Sound effects unavailable", error);
        }
    }

    boolean isMusicOn() {
        return musicOn;
    }

    boolean isEffectsOn() {
        return effectsOn;
    }

    void setMusicOn(boolean on) {
        musicOn = on;
        preferences.edit().putBoolean(MUSIC_ON, on).apply();
        restartMusic();
    }

    void setEffectsOn(boolean on) {
        effectsOn = on;
        preferences.edit().putBoolean(EFFECTS_ON, on).apply();
    }

    /** Switch to a tune (null or "" stops the music); the same tune keeps playing. */
    void playMusic(String name) {
        String wanted = name == null || name.isEmpty() ? null : name;
        if (wanted == null ? tune == null : wanted.equals(tune)) {
            return;
        }
        tune = wanted;
        Log.d(TAG, "music " + tune);
        restartMusic();
    }

    void playEffect(String name) {
        Integer id = effectIds.get(name);
        if (!effectsOn || !inForeground || id == null || !loadedEffects.contains(id)) {
            return;
        }
        long now = SystemClock.uptimeMillis();
        long at = Math.max(now, nextEffectAt);
        if (at - now > EFFECT_MAX_DELAY_MS) {
            return;
        }
        nextEffectAt = at + EFFECT_GAP_MS;
        handler.postAtTime(() -> {
            if (effectsOn && inForeground) {
                Log.d(TAG, "effect " + name);
                pool.play(id, 1f, 1f, 0, 0, 1f);
            }
        }, at);
    }

    void onPause() {
        inForeground = false;
        MediaPlayer playing = current();
        if (playing != null && playing.isPlaying()) {
            playing.pause();
        }
        pool.autoPause();
    }

    void onResume() {
        inForeground = true;
        pool.autoResume();
        MediaPlayer paused = current();
        if (paused != null) {
            paused.start();
        } else {
            restartMusic();
        }
    }

    void release() {
        stopMusic();
        handler.removeCallbacksAndMessages(null);
        pool.release();
    }

    private MediaPlayer current() {
        return intro != null ? intro : loop;
    }

    private void restartMusic() {
        stopMusic();
        if (tune == null || !musicOn || !inForeground) {
            return;
        }
        try {
            loop = open(tune + "_loop.ogg");
            loop.setLooping(true);
            intro = open(tune + "_intro.ogg");
            MediaPlayer started = intro;
            intro.setOnCompletionListener(player -> {
                player.release();
                if (intro == started) {
                    intro = null;
                }
            });
            intro.setNextMediaPlayer(loop);
            intro.start();
        } catch (IOException | RuntimeException error) {
            Log.w(TAG, "Cannot play tune " + tune, error);
            stopMusic();
        }
    }

    private MediaPlayer open(String file) throws IOException {
        MediaPlayer player = new MediaPlayer();
        try (AssetFileDescriptor fd = context.getAssets().openFd("audio/music/" + file)) {
            player.setAudioAttributes(new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_GAME)
                    .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                    .build());
            player.setDataSource(fd.getFileDescriptor(), fd.getStartOffset(), fd.getLength());
            player.setVolume(MUSIC_VOLUME, MUSIC_VOLUME);
            player.prepare();
        } catch (IOException | RuntimeException error) {
            player.release();
            throw error;
        }
        return player;
    }

    private void stopMusic() {
        if (intro != null) {
            intro.release();
            intro = null;
        }
        if (loop != null) {
            loop.release();
            loop = null;
        }
    }
}
