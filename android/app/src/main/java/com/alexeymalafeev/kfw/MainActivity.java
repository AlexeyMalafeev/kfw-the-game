package com.alexeymalafeev.kfw;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.database.Cursor;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.provider.OpenableColumns;
import android.text.InputType;
import android.util.Log;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputMethodManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Locale;

public final class MainActivity extends Activity {
    private static final String TAG = "KFW";
    private static final String PREFS = "kfw_preferences";
    private static final String LANGUAGE = "language";
    private static final String TEXT_SIZE = "text_size";
    private static final int REQUEST_IMPORT = 4101;
    private static final int REQUEST_EXPORT = 4102;

    private SharedPreferences preferences;
    private SaveRepository saves;
    private GameAudio audio;
    private GameHost currentHost;
    private Thread gameThread;
    private ConsoleView console;
    private LinearLayout choiceContainer;
    private ScrollView choiceScroll;
    private LinearLayout lineContainer;
    private EditText lineInput;
    private View inputPanel;
    private boolean mainVisible;
    private String pendingExport;
    private float textSize;

    @Override
    protected void attachBaseContext(Context base) {
        super.attachBaseContext(localizedContext(base));
    }

    private static Context localizedContext(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS, MODE_PRIVATE);
        String language = prefs.getString(LANGUAGE, null);
        if (language == null) {
            language = "ru".equals(Locale.getDefault().getLanguage()) ? "ru" : "en";
        }
        Configuration configuration = new Configuration(context.getResources().getConfiguration());
        configuration.setLocale(Locale.forLanguageTag(language));
        return context.createConfigurationContext(configuration);
    }

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        preferences = getSharedPreferences(PREFS, MODE_PRIVATE);
        String language = preferences.getString(LANGUAGE, null);
        if (language == null) {
            language = "ru".equals(Locale.getDefault().getLanguage()) ? "ru" : "en";
            preferences.edit().putString(LANGUAGE, language).apply();
        }
        textSize = preferences.getFloat(TEXT_SIZE, 13);
        saves = new SaveRepository(getFilesDir());
        audio = new GameAudio(this, preferences);
        showMain();
    }

    private String language() {
        return preferences.getString(LANGUAGE, "en");
    }

    private void showMain() {
        stopGameThread();
        mainVisible = true;
        console = null;
        choiceContainer = null;
        choiceScroll = null;
        lineContainer = null;
        lineInput = null;
        inputPanel = null;
        audio.playMusic(GameAudio.TITLE_TUNE);

        ScrollView scroll = new ScrollView(this);
        scroll.setId(R.id.main_root);
        scroll.setFillViewport(true);
        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setGravity(Gravity.CENTER_HORIZONTAL);
        content.setPadding(dp(24), dp(36), dp(24), dp(32));
        scroll.addView(content, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView title = new TextView(this);
        title.setText(R.string.title);
        title.setTextSize(32);
        title.setGravity(Gravity.CENTER);
        title.setTextColor(getColor(R.color.gold));
        title.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
        content.addView(title, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView subtitle = new TextView(this);
        subtitle.setText(R.string.subtitle);
        subtitle.setTextSize(16);
        subtitle.setGravity(Gravity.CENTER);
        subtitle.setPadding(0, dp(6), 0, dp(28));
        content.addView(subtitle);

        content.addView(menuButton(R.id.new_game, R.string.new_game,
                () -> startGame("new", null)));
        Button continueButton = menuButton(R.id.continue_game, R.string.continue_game, () -> {
            SaveRepository.SaveEntry latest = saves.latest();
            if (latest != null) {
                startGame("load", latest.name);
            }
        });
        continueButton.setEnabled(saves.latest() != null);
        content.addView(continueButton);
        Button loadButton = menuButton(R.id.load_game, R.string.load_game, this::showLoadDialog);
        loadButton.setEnabled(!saves.listSaves().isEmpty());
        content.addView(loadButton);
        content.addView(menuButton(R.id.watch_ai, R.string.watch_ai,
                () -> startGame("ai", null)));
        content.addView(menuButton(R.id.language_button, R.string.language,
                this::showLanguageDialog));
        content.addView(menuButton(R.id.import_save, R.string.import_save, this::launchImport));
        Button exportButton = menuButton(R.id.export_save, R.string.export_save,
                this::showExportDialog);
        exportButton.setEnabled(!saves.listSaves().isEmpty());
        content.addView(exportButton);
        content.addView(menuButton(R.id.about, R.string.about, this::showAbout));
        setContentView(scroll);
    }

    private Button menuButton(int id, int label, Runnable action) {
        Button button = new Button(this);
        button.setId(id);
        button.setText(label);
        button.setAllCaps(false);
        button.setTextSize(16);
        button.setMinHeight(dp(52));
        button.setOnClickListener(view -> action.run());
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        params.setMargins(0, dp(4), 0, dp(4));
        button.setLayoutParams(params);
        return button;
    }

    private void startGame(String mode, String saveName) {
        Thread previous = gameThread;
        stopGameThread();
        mainVisible = false;
        buildGameView();
        GameHost host = new GameHost(this);
        currentHost = host;
        console.append(getString(R.string.loading) + "\n");
        gameThread = new Thread(() -> {
            try {
                if (previous != null) {
                    previous.join(5000);
                    if (previous.isAlive()) {
                        throw new IllegalStateException("Previous game did not stop");
                    }
                }
                PyObject module = Python.getInstance().getModule("kfw_android");
                module.callAttr("run", host, mode, language(), saveName);
            } catch (Throwable error) {
                Log.e(TAG, "Python game failed", error);
                host.finished("error");
            }
        }, "KFW-Game");
        gameThread.setDaemon(true);
        gameThread.start();
    }

    private void buildGameView() {
        LinearLayout root = new LinearLayout(this);
        root.setId(R.id.game_root);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(getColor(R.color.ink));
        root.setOnApplyWindowInsetsListener((view, insets) -> {
            view.setPadding(0, insets.getSystemWindowInsetTop(), 0,
                    insets.getSystemWindowInsetBottom());
            return insets;
        });

        LinearLayout toolbar = new LinearLayout(this);
        toolbar.setOrientation(LinearLayout.HORIZONTAL);
        toolbar.setGravity(Gravity.CENTER_VERTICAL);
        toolbar.setPadding(dp(4), dp(2), dp(4), dp(2));
        toolbar.setBackgroundColor(getColor(R.color.panel));
        Button home = toolbarButton(R.id.home_button, "‹", R.string.main_menu);
        home.setTextSize(28);
        home.setOnClickListener(view -> confirmLeaveGame());
        toolbar.addView(home);
        TextView heading = new TextView(this);
        heading.setText(R.string.app_name);
        heading.setTextColor(getColor(R.color.gold));
        heading.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
        heading.setGravity(Gravity.CENTER);
        toolbar.addView(heading, new LinearLayout.LayoutParams(0,
                ViewGroup.LayoutParams.WRAP_CONTENT, 1));
        Button smaller = toolbarButton(R.id.text_smaller, "A−", R.string.text_smaller);
        smaller.setOnClickListener(view -> changeTextSize(-1));
        toolbar.addView(smaller);
        Button larger = toolbarButton(R.id.text_larger, "A+", R.string.text_larger);
        larger.setOnClickListener(view -> changeTextSize(1));
        toolbar.addView(larger);
        Button musicToggle = toolbarButton(R.id.music_toggle, "♪", R.string.music_toggle);
        musicToggle.setOnClickListener(view -> {
            audio.setMusicOn(!audio.isMusicOn());
            showToggle(musicToggle, R.string.music_toggle, audio.isMusicOn());
        });
        showToggle(musicToggle, R.string.music_toggle, audio.isMusicOn());
        toolbar.addView(musicToggle);
        Button effectsToggle = toolbarButton(R.id.effects_toggle, "FX", R.string.effects_toggle);
        effectsToggle.setOnClickListener(view -> {
            audio.setEffectsOn(!audio.isEffectsOn());
            showToggle(effectsToggle, R.string.effects_toggle, audio.isEffectsOn());
        });
        showToggle(effectsToggle, R.string.effects_toggle, audio.isEffectsOn());
        toolbar.addView(effectsToggle);
        root.addView(toolbar, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(52)));

        console = new ConsoleView(this);
        console.setConsoleTextSize(textSize);
        root.addView(console, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, 0, 1));

        inputPanel = new LinearLayout(this);
        ((LinearLayout) inputPanel).setOrientation(LinearLayout.VERTICAL);
        inputPanel.setBackgroundColor(getColor(R.color.panel));
        inputPanel.setVisibility(View.GONE);

        choiceScroll = new ScrollView(this);
        choiceScroll.setId(R.id.input_scroll);
        choiceContainer = new LinearLayout(this);
        choiceContainer.setId(R.id.input_container);
        choiceContainer.setOrientation(LinearLayout.VERTICAL);
        choiceContainer.setPadding(dp(6), dp(4), dp(6), dp(6));
        choiceScroll.addView(choiceContainer);
        ((LinearLayout) inputPanel).addView(choiceScroll);

        lineContainer = new LinearLayout(this);
        lineContainer.setId(R.id.line_container);
        lineContainer.setOrientation(LinearLayout.HORIZONTAL);
        lineContainer.setGravity(Gravity.CENTER_VERTICAL);
        lineContainer.setPadding(dp(8), dp(6), dp(8), dp(8));
        lineInput = new EditText(this);
        lineInput.setId(R.id.line_input);
        lineInput.setHint(R.string.text_input_hint);
        lineInput.setSingleLine(true);
        lineInput.setInputType(InputType.TYPE_CLASS_TEXT);
        lineInput.setImeOptions(EditorInfo.IME_ACTION_DONE);
        lineInput.setOnEditorActionListener((view, actionId, event) -> {
            if (actionId == EditorInfo.IME_ACTION_DONE) {
                submitCurrentLine();
                return true;
            }
            return false;
        });
        lineContainer.addView(lineInput, new LinearLayout.LayoutParams(0, dp(52), 1));
        Button send = new Button(this);
        send.setId(R.id.send_button);
        send.setText(R.string.send);
        send.setOnClickListener(view -> submitCurrentLine());
        lineContainer.addView(send);
        ((LinearLayout) inputPanel).addView(lineContainer);
        root.addView(inputPanel, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        setContentView(root);
    }

    private Button toolbarButton(int id, String text, int description) {
        Button button = new Button(this);
        button.setId(id);
        button.setText(text);
        button.setContentDescription(getString(description));
        button.setAllCaps(false);
        button.setMinWidth(dp(48));
        button.setMinimumHeight(dp(48));
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                dp(58), ViewGroup.LayoutParams.WRAP_CONTENT);
        button.setLayoutParams(params);
        return button;
    }

    /** A toolbar on/off toggle: dimmed when off; the state is also announced. */
    private void showToggle(Button button, int label, boolean on) {
        button.setAlpha(on ? 1f : 0.35f);
        button.setContentDescription(getString(R.string.toggle_state, getString(label),
                getString(on ? R.string.state_on : R.string.state_off)));
    }

    void playMusic(GameHost source, String tune) {
        runOnUiThread(() -> {
            if (source == currentHost) {
                audio.playMusic(tune);
            }
        });
    }

    void playSound(GameHost source, String effect) {
        runOnUiThread(() -> {
            if (source == currentHost) {
                audio.playEffect(effect);
            }
        });
    }

    void appendConsole(GameHost source, String text) {
        runOnUiThread(() -> {
            if (source == currentHost && console != null) {
                console.append(text);
            }
        });
    }

    void clearConsole(GameHost source) {
        runOnUiThread(() -> {
            if (source == currentHost && console != null) {
                console.clear();
            }
        });
    }

    void showKeyInput(GameHost source, String keys, List<String> labels, boolean weak) {
        runOnUiThread(() -> {
            if (source != currentHost || choiceContainer == null) {
                return;
            }
            hideSoftKeyboard();
            lineContainer.setVisibility(View.GONE);
            choiceScroll.setVisibility(View.VISIBLE);
            inputPanel.setVisibility(View.VISIBLE);
            choiceContainer.removeAllViews();
            if (keys == null || labels == null) {
                Button proceed = choiceButton(R.string.continue_input, "continue", null);
                proceed.setId(R.id.continue_button);
                proceed.setOnClickListener(view -> {
                    source.submitKey(" ");
                    hideInput(source);
                });
                choiceContainer.addView(proceed);
                choiceScroll.setLayoutParams(new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
                return;
            }
            for (int i = 0; i < labels.size(); i++) {
                String key = String.valueOf(keys.charAt(i));
                String label = labels.get(i);
                Button button = choiceButton(0, "choice:" + key, label);
                button.setText(getString(R.string.menu_option, key, label));
                button.setOnClickListener(view -> {
                    source.submitKey(key);
                    hideInput(source);
                });
                choiceContainer.addView(button);
            }
            if (weak) {
                Button back = choiceButton(R.string.dismiss_menu, "choice:\u001b",
                        getString(R.string.dismiss_menu));
                back.setId(R.id.dismiss_menu);
                back.setOnClickListener(view -> {
                    source.submitKey("\u001b");
                    hideInput(source);
                });
                choiceContainer.addView(back);
            }
            int height = labels.size() > 5 ? dp(280) : ViewGroup.LayoutParams.WRAP_CONTENT;
            choiceScroll.setLayoutParams(new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, height));
        });
    }

    private Button choiceButton(int textResource, String tag, String description) {
        Button button = new Button(this);
        if (textResource != 0) {
            button.setText(textResource);
        }
        button.setTag(tag);
        if (description != null) {
            button.setContentDescription(description);
        }
        button.setAllCaps(false);
        button.setGravity(Gravity.START | Gravity.CENTER_VERTICAL);
        button.setTextSize(14);
        button.setMinHeight(dp(48));
        button.setPadding(dp(12), 0, dp(8), 0);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        params.setMargins(0, dp(2), 0, dp(2));
        button.setLayoutParams(params);
        return button;
    }

    void showLineInput(GameHost source) {
        runOnUiThread(() -> {
            if (source != currentHost || lineContainer == null) {
                return;
            }
            choiceScroll.setVisibility(View.GONE);
            lineContainer.setVisibility(View.VISIBLE);
            inputPanel.setVisibility(View.VISIBLE);
            lineInput.setText("");
            lineInput.requestFocus();
            lineInput.post(() -> {
                InputMethodManager keyboard =
                        (InputMethodManager) getSystemService(INPUT_METHOD_SERVICE);
                keyboard.showSoftInput(lineInput, InputMethodManager.SHOW_IMPLICIT);
            });
        });
    }

    private void submitCurrentLine() {
        GameHost host = currentHost;
        if (host != null && lineInput != null) {
            host.submitLine(lineInput.getText().toString());
            hideInput(host);
        }
    }

    void hideInput(GameHost source) {
        runOnUiThread(() -> {
            if (source != currentHost) {
                return;
            }
            hideSoftKeyboard();
            if (inputPanel != null) {
                inputPanel.setVisibility(View.GONE);
            }
        });
    }

    void gameFinished(GameHost source, String status) {
        runOnUiThread(() -> {
            if (source != currentHost) {
                return;
            }
            source.close();
            if ("error".equals(status)) {
                new AlertDialog.Builder(this)
                        .setTitle(R.string.error_title)
                        .setMessage(R.string.error_emergency)
                        .setPositiveButton(R.string.main_menu, (dialog, which) -> showMain())
                        .setOnDismissListener(dialog -> {
                            if (!mainVisible) {
                                showMain();
                            }
                        })
                        .show();
            } else {
                Toast.makeText(this, R.string.game_finished, Toast.LENGTH_SHORT).show();
                showMain();
            }
        });
    }

    private void stopGameThread() {
        GameHost old = currentHost;
        currentHost = null;
        if (old != null) {
            old.close();
        }
    }

    private void confirmLeaveGame() {
        new AlertDialog.Builder(this)
                .setTitle(R.string.quit_to_title)
                .setMessage(R.string.unsaved_warning)
                .setNegativeButton(R.string.cancel, null)
                .setPositiveButton(R.string.leave_without_saving,
                        (dialog, which) -> showMain())
                .show();
    }

    private void changeTextSize(float delta) {
        textSize = Math.max(8, Math.min(24, textSize + delta));
        preferences.edit().putFloat(TEXT_SIZE, textSize).apply();
        if (console != null) {
            console.setConsoleTextSize(textSize);
        }
    }

    private void showLoadDialog() {
        List<SaveRepository.SaveEntry> entries = saves.listSaves();
        if (entries.isEmpty()) {
            Toast.makeText(this, R.string.no_saves, Toast.LENGTH_SHORT).show();
            return;
        }
        String[] labels = entryLabels(entries);
        new AlertDialog.Builder(this)
                .setTitle(R.string.choose_save)
                .setItems(labels, (dialog, which) -> startGame("load", entries.get(which).name))
                .setNegativeButton(R.string.cancel, null)
                .show();
    }

    private void showExportDialog() {
        List<SaveRepository.SaveEntry> entries = saves.listSaves();
        if (entries.isEmpty()) {
            Toast.makeText(this, R.string.no_saves, Toast.LENGTH_SHORT).show();
            return;
        }
        new AlertDialog.Builder(this)
                .setTitle(R.string.export_save)
                .setItems(entryLabels(entries), (dialog, which) -> {
                    pendingExport = entries.get(which).name;
                    Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                    intent.addCategory(Intent.CATEGORY_OPENABLE);
                    intent.setType("text/plain");
                    intent.putExtra(Intent.EXTRA_TITLE, pendingExport);
                    startActivityForResult(intent, REQUEST_EXPORT);
                })
                .setNegativeButton(R.string.cancel, null)
                .show();
    }

    private static String[] entryLabels(List<SaveRepository.SaveEntry> entries) {
        String[] labels = new String[entries.size()];
        for (int i = 0; i < entries.size(); i++) {
            labels[i] = entries.get(i).displayName();
        }
        return labels;
    }

    private void launchImport() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        startActivityForResult(intent, REQUEST_IMPORT);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode != RESULT_OK || data == null || data.getData() == null) {
            return;
        }
        Uri uri = data.getData();
        try {
            if (requestCode == REQUEST_IMPORT) {
                try (InputStream input = getContentResolver().openInputStream(uri)) {
                    saves.importSave(input, displayName(uri));
                }
                Toast.makeText(this, R.string.save_imported, Toast.LENGTH_SHORT).show();
            } else if (requestCode == REQUEST_EXPORT && pendingExport != null) {
                try (java.io.OutputStream output = getContentResolver().openOutputStream(uri, "wt")) {
                    saves.exportSave(pendingExport, output);
                }
                Toast.makeText(this, R.string.save_exported, Toast.LENGTH_SHORT).show();
            }
        } catch (Exception error) {
            Log.e(TAG, "Save transfer failed", error);
            Toast.makeText(this, requestCode == REQUEST_IMPORT
                    ? R.string.import_failed : R.string.export_failed, Toast.LENGTH_LONG).show();
        } finally {
            pendingExport = null;
            if (mainVisible) {
                showMain();
            }
        }
    }

    private String displayName(Uri uri) {
        try (Cursor cursor = getContentResolver().query(uri, null, null, null, null)) {
            if (cursor != null && cursor.moveToFirst()) {
                int column = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                if (column >= 0) {
                    return cursor.getString(column);
                }
            }
        }
        return uri.getLastPathSegment();
    }

    private void showLanguageDialog() {
        String[] languages = {"English", "Русский"};
        new AlertDialog.Builder(this)
                .setTitle(R.string.choose_language)
                .setItems(languages, (dialog, which) -> {
                    String selected = which == 1 ? "ru" : "en";
                    if (!selected.equals(language())) {
                        preferences.edit().putString(LANGUAGE, selected).apply();
                        Toast.makeText(this, R.string.language_restart, Toast.LENGTH_SHORT).show();
                        new Handler().postDelayed(this::restartApplication, 350);
                    }
                })
                .setNegativeButton(R.string.cancel, null)
                .show();
    }

    private void restartApplication() {
        Intent intent = getPackageManager().getLaunchIntentForPackage(getPackageName());
        if (intent != null) {
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            startActivity(intent);
        }
        Runtime.getRuntime().halt(0);
    }

    private void showAbout() {
        new AlertDialog.Builder(this)
                .setTitle(R.string.about)
                .setMessage(R.string.about_text)
                .setPositiveButton(R.string.ok, null)
                .setNeutralButton(R.string.license_title,
                        (dialog, which) -> showTextAsset(R.string.license_title, "LICENSE.txt"))
                .setNegativeButton(R.string.third_party_licenses,
                        (dialog, which) -> showThirdPartyLicenses())
                .show();
    }

    private void showThirdPartyLicenses() {
        String[] names = {"Chaquopy", "CPython"};
        String[] files = {"CHAQUOPY_LICENSE.txt", "PYTHON_LICENSE.txt"};
        new AlertDialog.Builder(this)
                .setTitle(R.string.third_party_licenses)
                .setItems(names, (dialog, which) ->
                        showTextAsset(R.string.third_party_licenses, files[which]))
                .setNegativeButton(R.string.cancel, null)
                .show();
    }

    private void showTextAsset(int title, String fileName) {
        StringBuilder text = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(
                getAssets().open(fileName), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                text.append(line).append('\n');
            }
        } catch (IOException error) {
            text.append(error.getMessage());
        }
        new AlertDialog.Builder(this)
                .setTitle(title)
                .setMessage(text.toString())
                .setPositiveButton(R.string.ok, null)
                .show();
    }

    private void hideSoftKeyboard() {
        if (lineInput == null) {
            return;
        }
        InputMethodManager keyboard = (InputMethodManager) getSystemService(INPUT_METHOD_SERVICE);
        keyboard.hideSoftInputFromWindow(lineInput.getWindowToken(), 0);
        lineInput.clearFocus();
    }

    @Override
    public boolean dispatchKeyEvent(KeyEvent event) {
        GameHost host = currentHost;
        if (host != null && host.isAwaitingKey()
                && (lineInput == null || !lineInput.hasFocus())
                && event.getKeyCode() != KeyEvent.KEYCODE_BACK
                && event.getAction() == KeyEvent.ACTION_UP) {
            String key = null;
            if (event.getKeyCode() == KeyEvent.KEYCODE_ENTER
                    || event.getKeyCode() == KeyEvent.KEYCODE_NUMPAD_ENTER) {
                key = "\n";
            } else if (event.getKeyCode() == KeyEvent.KEYCODE_ESCAPE) {
                key = "\u001b";
            } else {
                int codePoint = event.getUnicodeChar();
                if (codePoint > 0 && !Character.isISOControl(codePoint)) {
                    key = new String(Character.toChars(codePoint));
                }
            }
            if (key != null) {
                host.submitKey(key);
                return true;
            }
        }
        return super.dispatchKeyEvent(event);
    }

    @Override
    public void onBackPressed() {
        if (!mainVisible && currentHost != null) {
            confirmLeaveGame();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onPause() {
        audio.onPause();
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        audio.onResume();
    }

    @Override
    protected void onDestroy() {
        // A recreated activity starts at the title and cannot reattach to the old
        // game, so always stop it rather than leave its thread blocked on input.
        stopGameThread();
        audio.release();
        super.onDestroy();
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
