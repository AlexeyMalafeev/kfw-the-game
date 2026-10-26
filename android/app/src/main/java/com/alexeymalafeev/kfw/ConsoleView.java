package com.alexeymalafeev.kfw;

import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.text.Editable;
import android.text.Spanned;
import android.text.style.ForegroundColorSpan;
import android.text.style.StyleSpan;
import android.view.Gravity;
import android.view.View;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.util.List;

public final class ConsoleView extends LinearLayout {
    private static final int MAX_CHARACTERS = 400_000;
    private final AnsiParser parser = new AnsiParser();
    private final Editable content;
    private final ScrollView verticalScroll;
    private final HorizontalScrollView horizontalScroll;
    private final TextView textView;

    public ConsoleView(Context context) {
        super(context);
        setOrientation(VERTICAL);
        setBackgroundColor(Color.rgb(16, 19, 18));

        verticalScroll = new ScrollView(context);
        verticalScroll.setId(R.id.console_scroll);
        verticalScroll.setFillViewport(true);
        horizontalScroll = new HorizontalScrollView(context);
        horizontalScroll.setFillViewport(true);
        horizontalScroll.setHorizontalScrollBarEnabled(true);
        textView = new TextView(context);
        textView.setId(R.id.console);
        textView.setTypeface(Typeface.MONOSPACE);
        textView.setTextColor(Color.rgb(236, 237, 230));
        textView.setTextSize(13);
        textView.setGravity(Gravity.TOP | Gravity.START);
        textView.setPadding(dp(10), dp(8), dp(10), dp(16));
        textView.setTextIsSelectable(true);
        textView.setShowSoftInputOnFocus(false);
        textView.setHorizontallyScrolling(true);
        textView.setText("", TextView.BufferType.EDITABLE);
        content = textView.getEditableText();

        horizontalScroll.addView(textView, new HorizontalScrollView.LayoutParams(
                LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT));
        verticalScroll.addView(horizontalScroll, new ScrollView.LayoutParams(
                LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT));
        addView(verticalScroll, new LinearLayout.LayoutParams(
                LayoutParams.MATCH_PARENT, 0, 1));
    }

    public void append(String text) {
        boolean follow = isNearBottom();
        List<AnsiParser.Segment> segments = parser.parse(text);
        for (AnsiParser.Segment segment : segments) {
            int start = content.length();
            content.append(segment.text);
            int end = content.length();
            AnsiParser.Style style = segment.style;
            int color = colorFor(style.color);
            if (style.dim) {
                color = Color.argb(165, Color.red(color), Color.green(color), Color.blue(color));
            }
            content.setSpan(new ForegroundColorSpan(color), start, end,
                    Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            if (style.bold) {
                content.setSpan(new StyleSpan(Typeface.BOLD), start, end,
                        Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            }
            if (style.italic) {
                content.setSpan(new StyleSpan(Typeface.ITALIC), start, end,
                        Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            }
        }
        trimHistory();
        if (follow) {
            verticalScroll.post(() -> verticalScroll.fullScroll(View.FOCUS_DOWN));
        }
    }

    public void clear() {
        content.clear();
        horizontalScroll.scrollTo(0, 0);
        verticalScroll.scrollTo(0, 0);
    }

    public void setConsoleTextSize(float sizeSp) {
        textView.setTextSize(sizeSp);
    }

    public String getPlainText() {
        return content.toString();
    }

    private boolean isNearBottom() {
        View child = verticalScroll.getChildAt(0);
        if (child == null || verticalScroll.getHeight() == 0) {
            return true;
        }
        return verticalScroll.getScrollY() + verticalScroll.getHeight()
                >= child.getHeight() - dp(48);
    }

    private void trimHistory() {
        int excess = content.length() - MAX_CHARACTERS;
        if (excess <= 0) {
            return;
        }
        int newline = content.toString().indexOf('\n', excess);
        content.delete(0, newline >= 0 ? newline + 1 : excess);
    }

    private int colorFor(int ansi) {
        switch (ansi) {
            case 30: return Color.rgb(70, 76, 73);
            case 31: return Color.rgb(239, 106, 100);
            case 32: return Color.rgb(143, 203, 127);
            case 33: return Color.rgb(230, 184, 92);
            case 34: return Color.rgb(126, 166, 224);
            case 35: return Color.rgb(217, 140, 211);
            case 36: return Color.rgb(105, 197, 200);
            case 90: return Color.rgb(142, 153, 146);
            case 91: return Color.rgb(255, 120, 114);
            case 92: return Color.rgb(160, 225, 140);
            case 93: return Color.rgb(245, 205, 110);
            case 94: return Color.rgb(145, 185, 240);
            case 95: return Color.rgb(232, 155, 225);
            case 96: return Color.rgb(120, 215, 218);
            case 97:
            case 37:
            default: return Color.rgb(236, 237, 230);
        }
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
