package com.alexeymalafeev.kfw;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public final class SaveRepository {
    public static final int MAX_SAVE_BYTES = 20 * 1024 * 1024;

    public static final class SaveEntry {
        public final String name;
        public final long modified;
        public final boolean legacy;

        SaveEntry(String name, long modified, boolean legacy) {
            this.name = name;
            this.modified = modified;
            this.legacy = legacy;
        }

        public String displayName() {
            String suffix = legacy ? " (legacy)" : "";
            return name + suffix;
        }
    }

    private final File directory;

    public SaveRepository(File filesDirectory) {
        directory = new File(filesDirectory, "save");
        if (!directory.exists() && !directory.mkdirs()) {
            throw new IllegalStateException("Cannot create save directory: " + directory);
        }
    }

    public List<SaveEntry> listSaves() {
        File[] files = directory.listFiles();
        if (files == null) {
            return Collections.emptyList();
        }
        Arrays.sort(files, Comparator.comparingLong(File::lastModified).reversed());
        List<SaveEntry> result = new ArrayList<>();
        for (File file : files) {
            if (!file.isFile() || file.length() > MAX_SAVE_BYTES) {
                continue;
            }
            try {
                Boolean legacy = validate(readFile(file));
                if (legacy != null) {
                    result.add(new SaveEntry(file.getName(), file.lastModified(), legacy));
                }
            } catch (IOException ignored) {
                // A partially written or unreadable file is not offered for loading.
            }
        }
        return result;
    }

    public SaveEntry latest() {
        List<SaveEntry> saves = listSaves();
        return saves.isEmpty() ? null : saves.get(0);
    }

    public File get(String name) throws IOException {
        File parent = directory.getCanonicalFile();
        File file = new File(parent, name).getCanonicalFile();
        if (!file.getParentFile().equals(parent) || !file.isFile()) {
            throw new IOException("Invalid save file: " + name);
        }
        return file;
    }

    public SaveEntry importSave(InputStream input, String originalName) throws IOException {
        byte[] data = readLimited(input);
        if (validate(data) == null) {
            throw new IOException("Not a KFW save");
        }
        String name = availableName(sanitizeName(originalName));
        File output = new File(directory, name);
        try (FileOutputStream stream = new FileOutputStream(output, false)) {
            stream.write(data);
        }
        return new SaveEntry(name, output.lastModified(), validate(data));
    }

    public void exportSave(String name, OutputStream output) throws IOException {
        try (InputStream input = new FileInputStream(get(name))) {
            byte[] buffer = new byte[16 * 1024];
            int count;
            while ((count = input.read(buffer)) >= 0) {
                output.write(buffer, 0, count);
            }
        }
    }

    public static String sanitizeName(String original) {
        String name = original == null ? "" : new File(original).getName();
        name = name.replaceAll("[<>:\"/\\\\|?*\\p{Cntrl}]", "_").trim();
        while (name.startsWith(".")) {
            name = name.substring(1);
        }
        if (name.isEmpty()) {
            name = "imported-save";
        }
        if (!name.toLowerCase(java.util.Locale.ROOT).endsWith(".txt")) {
            name += ".txt";
        }
        if (name.length() > 100) {
            name = name.substring(0, 96) + ".txt";
        }
        return name;
    }

    private String availableName(String name) {
        String base = name.substring(0, name.length() - 4);
        File candidate = new File(directory, name);
        int index = 1;
        while (candidate.exists()) {
            candidate = new File(directory, base + "-" + index + ".txt");
            index++;
        }
        return candidate.getName();
    }

    private static byte[] readFile(File file) throws IOException {
        try (InputStream input = new FileInputStream(file)) {
            return readLimited(input);
        }
    }

    private static byte[] readLimited(InputStream input) throws IOException {
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        byte[] buffer = new byte[16 * 1024];
        int total = 0;
        int count;
        while ((count = input.read(buffer)) >= 0) {
            total += count;
            if (total > MAX_SAVE_BYTES) {
                throw new IOException("Save is too large");
            }
            output.write(buffer, 0, count);
        }
        return output.toByteArray();
    }

    private static Boolean validate(byte[] data) {
        String text = new String(data, StandardCharsets.UTF_8).trim();
        if (text.startsWith("{")) {
            try {
                JSONObject object = new JSONObject(text);
                if ("kfw-save".equals(object.optString("format"))
                        && object.optInt("version", 0) >= 1
                        && object.has("fighters") && object.has("players")
                        && object.has("game_atts")) {
                    return false;
                }
            } catch (Exception ignored) {
                return null;
            }
        }
        if (text.contains("g.fighters_dict") && text.contains("g.players")) {
            return true;
        }
        return null;
    }
}
