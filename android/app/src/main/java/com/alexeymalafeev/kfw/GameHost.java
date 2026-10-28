package com.alexeymalafeev.kfw;

import org.json.JSONArray;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

public final class GameHost {
    private static final int KEY = 1;
    private static final int LINE = 2;

    private static final class Input {
        final int kind;
        final String value;

        Input(int kind, String value) {
            this.kind = kind;
            this.value = value;
        }
    }

    private final MainActivity activity;
    private final BlockingQueue<Input> inputs = new LinkedBlockingQueue<>();
    private volatile boolean closed;
    private volatile int inputKind;
    private String pendingKeys;
    private List<String> pendingLabels;
    private boolean pendingWeak;

    GameHost(MainActivity activity) {
        this.activity = activity;
    }

    public boolean isClosed() {
        return closed;
    }

    public boolean isAwaitingKey() {
        return !closed && inputKind == KEY;
    }

    public void write(String text) {
        if (!closed) {
            activity.appendConsole(this, text);
        }
    }

    public void clear() {
        if (!closed) {
            activity.clearConsole(this);
        }
    }

    public void playMusic(String tune) {
        if (!closed) {
            activity.playMusic(this, tune);
        }
    }

    public void playSound(String effect) {
        if (!closed) {
            activity.playSound(this, effect);
        }
    }

    public synchronized void presentMenu(String keys, String labelsJson, boolean weak) {
        if (closed) {
            return;
        }
        try {
            JSONArray array = new JSONArray(labelsJson);
            List<String> labels = new ArrayList<>();
            for (int i = 0; i < array.length(); i++) {
                labels.add(array.getString(i));
            }
            if (keys.length() != labels.size()) {
                throw new IllegalArgumentException("Menu keys and labels differ in length");
            }
            pendingKeys = keys;
            pendingLabels = labels;
            pendingWeak = weak;
        } catch (Exception error) {
            pendingKeys = null;
            pendingLabels = null;
            throw new IllegalArgumentException("Invalid menu from Python", error);
        }
    }

    public String readKey() {
        final String keys;
        final List<String> labels;
        final boolean weak;
        synchronized (this) {
            keys = pendingKeys;
            labels = pendingLabels;
            weak = pendingWeak;
            pendingKeys = null;
            pendingLabels = null;
            pendingWeak = false;
        }
        Input input = await(KEY, keys, labels, weak);
        return input != null && input.kind == KEY ? input.value : null;
    }

    public String readLine() {
        Input input = await(LINE, null, null, false);
        return input != null && input.kind == LINE ? input.value : null;
    }

    private Input await(int kind, String keys, List<String> labels, boolean weak) {
        if (closed) {
            return null;
        }
        inputs.clear();
        inputKind = kind;
        if (kind == KEY) {
            activity.showKeyInput(this, keys, labels, weak);
        } else {
            activity.showLineInput(this);
        }
        try {
            while (!closed) {
                Input input = inputs.take();
                if (input.kind == kind) {
                    return input;
                }
            }
        } catch (InterruptedException error) {
            Thread.currentThread().interrupt();
        } finally {
            inputKind = 0;
        }
        return null;
    }

    public void submitKey(String key) {
        if (!closed && inputKind == KEY) {
            inputs.offer(new Input(KEY, key));
        }
    }

    public void submitLine(String line) {
        if (!closed && inputKind == LINE) {
            inputs.offer(new Input(LINE, line));
        }
    }

    public void finished(String status) {
        inputKind = 0;
        activity.gameFinished(this, status);
    }

    public void close() {
        if (closed) {
            return;
        }
        closed = true;
        inputKind = 0;
        inputs.clear();
        inputs.offer(new Input(0, ""));
        activity.hideInput(this);
    }
}
