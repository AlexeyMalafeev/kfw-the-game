package com.alexeymalafeev.kfw;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

import java.util.Arrays;

import org.junit.Test;

public class LineWrapperTest {
    private static float[] widths(String line) {
        float[] result = new float[line.length()];
        Arrays.fill(result, 1f);
        return result;
    }

    private static String wrap(String line, float maxWidth) {
        int[] breaks = LineWrapper.breaks(line, widths(line), maxWidth);
        String indent = line.substring(0, LineWrapper.indentLength(line));
        StringBuilder result = new StringBuilder(line);
        for (int i = breaks.length - 1; i >= 0; i--) {
            result.replace(breaks[i], breaks[i] + 1, "\n" + indent);
        }
        return result.toString();
    }

    @Test
    public void shortLinesStayWhole() {
        assertArrayEquals(new int[0], LineWrapper.breaks("Practices at school.",
                widths("Practices at school."), 20));
    }

    @Test
    public void proseWrapsAtSpacesWithinWidth() {
        String wrapped = wrap("Is about to propose to Wu Chengpeng, but gets cold feet.", 20);
        assertEquals("Is about to propose\nto Wu Chengpeng, but\ngets cold feet.", wrapped);
        for (String line : wrapped.split("\n")) {
            assertEquals(true, line.length() <= 20);
        }
    }

    @Test
    public void continuationLinesKeepTheIndent() {
        assertEquals("  one two\n  three four", wrap("  one two three four", 12));
    }

    @Test
    public void wordLongerThanWidthIsNotSplit() {
        assertEquals("a\nextraordinarily\nlong", wrap("a extraordinarily long", 8));
    }

    @Test
    public void preformattedLinesAreNotWrapped() {
        String panel = "Han Yan        Cai Tofu HP %%%%%%%%%% 120";
        assertArrayEquals(new int[0], LineWrapper.breaks(panel, widths(panel), 10));
        String bars = "HP %%%%%%%%%% 120 160 %%%%%%%%%% HP";
        assertArrayEquals(new int[0], LineWrapper.breaks(bars, widths(bars), 10));
    }

    @Test
    public void ellipsisDoesNotMarkProseAsPreformatted() {
        assertEquals("Wait... let\nus talk", wrap("Wait... let us talk", 12));
    }

    @Test
    public void unknownWidthDisablesWrapping() {
        String line = "one two three four";
        assertArrayEquals(new int[0], LineWrapper.breaks(line, widths(line), 0));
    }
}
