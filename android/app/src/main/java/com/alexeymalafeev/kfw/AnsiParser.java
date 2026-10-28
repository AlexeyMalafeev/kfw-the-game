package com.alexeymalafeev.kfw;

import java.util.ArrayList;
import java.util.List;

public final class AnsiParser {
    public static final class Style {
        public int color = -1;
        public boolean bold;
        public boolean dim;
        public boolean italic;

        public Style copy() {
            Style result = new Style();
            result.color = color;
            result.bold = bold;
            result.dim = dim;
            result.italic = italic;
            return result;
        }
    }

    public static final class Segment {
        public final String text;
        public final Style style;

        Segment(String text, Style style) {
            this.text = text;
            this.style = style;
        }
    }

    private Style current = new Style();
    private String pending = "";

    public List<Segment> parse(String chunk) {
        String input = pending + chunk;
        pending = "";
        List<Segment> result = new ArrayList<>();
        int position = 0;
        while (position < input.length()) {
            int escape = input.indexOf("\u001b[", position);
            if (escape < 0) {
                addSegment(result, input.substring(position));
                break;
            }
            if (escape > position) {
                addSegment(result, input.substring(position, escape));
            }
            int end = input.indexOf('m', escape + 2);
            if (end < 0) {
                pending = input.substring(escape);
                break;
            }
            applySgr(input.substring(escape + 2, end));
            position = end + 1;
        }
        return result;
    }

    private void addSegment(List<Segment> result, String text) {
        if (text.isEmpty()) {
            return;
        }
        Style style = current.copy();
        int last = result.size() - 1;
        if (last >= 0) {
            Segment previous = result.get(last);
            Style old = previous.style;
            if (old.color == style.color && old.bold == style.bold
                    && old.dim == style.dim && old.italic == style.italic) {
                result.set(last, new Segment(previous.text + text, old));
                return;
            }
        }
        result.add(new Segment(text, style));
    }

    private void applySgr(String parameters) {
        if (parameters.isEmpty()) {
            current = new Style();
            return;
        }
        String[] codes = parameters.split(";", -1);
        for (String rawCode : codes) {
            final int code;
            try {
                code = rawCode.isEmpty() ? 0 : Integer.parseInt(rawCode);
            } catch (NumberFormatException ignored) {
                continue;
            }
            if (code == 0) {
                current = new Style();
            } else if (code == 1) {
                current.bold = true;
            } else if (code == 2) {
                current.dim = true;
            } else if (code == 3) {
                current.italic = true;
            } else if (code == 22) {
                current.bold = false;
                current.dim = false;
            } else if (code == 23) {
                current.italic = false;
            } else if ((code >= 30 && code <= 37) || (code >= 90 && code <= 97)) {
                current.color = code;
            } else if (code == 39) {
                current.color = -1;
            }
        }
    }
}
