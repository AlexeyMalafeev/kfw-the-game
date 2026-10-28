package com.alexeymalafeev.kfw;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

/**
 * Word-wraps one console line to a pixel width. Lines that use runs of spaces for
 * layout (tables, fighter panels) or runs of a symbol (ASCII art, HP bars) are left
 * alone and scroll horizontally.
 */
public final class LineWrapper {
    private static final Pattern PREFORMATTED = Pattern.compile("\\S {2,}\\S|([^\\w\\s.])\\1\\1");

    private LineWrapper() {
    }

    /** Returns the indices of the spaces to replace with line breaks. */
    public static int[] breaks(String line, float[] charWidths, float maxWidth) {
        if (maxWidth <= 0 || PREFORMATTED.matcher(line).find()) {
            return new int[0];
        }
        float total = 0;
        for (int i = 0; i < line.length(); i++) {
            total += charWidths[i];
        }
        if (total <= maxWidth) {
            return new int[0];
        }
        int indentLength = indentLength(line);
        float indentWidth = 0;
        for (int i = 0; i < indentLength; i++) {
            indentWidth += charWidths[i];
        }
        List<Integer> result = new ArrayList<>();
        float width = 0;
        int lastSpace = -1;
        float widthAtLastSpace = 0;
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (c == ' ' && i >= indentLength) {
                lastSpace = i;
                widthAtLastSpace = width;
            }
            width += charWidths[i];
            if (width > maxWidth && c != ' ' && lastSpace >= 0) {
                // break at the last space; the rest of the line starts after the indent
                result.add(lastSpace);
                width = indentWidth + width - widthAtLastSpace - charWidths[lastSpace];
                lastSpace = -1;
            }
        }
        int[] array = new int[result.size()];
        for (int i = 0; i < array.length; i++) {
            array[i] = result.get(i);
        }
        return array;
    }

    public static int indentLength(String line) {
        int i = 0;
        while (i < line.length() && line.charAt(i) == ' ') {
            i++;
        }
        // an all-blank line or an indent wider than half the line is not a paragraph
        return i * 2 > line.length() ? 0 : i;
    }
}
