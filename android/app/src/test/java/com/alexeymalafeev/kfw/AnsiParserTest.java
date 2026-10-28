package com.alexeymalafeev.kfw;

import org.junit.Test;

import java.util.List;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public class AnsiParserTest {
    @Test
    public void plainTextKeepsDefaultStyle() {
        List<AnsiParser.Segment> result = new AnsiParser().parse("plain\n");

        assertEquals(1, result.size());
        assertEquals("plain\n", result.get(0).text);
        assertEquals(-1, result.get(0).style.color);
        assertFalse(result.get(0).style.bold);
    }

    @Test
    public void colorsAndResetAreApplied() {
        List<AnsiParser.Segment> result = new AnsiParser().parse(
                "\u001b[31mred\u001b[0m plain\u001b[1;32mbold green");

        assertEquals(3, result.size());
        assertEquals("red", result.get(0).text);
        assertEquals(31, result.get(0).style.color);
        assertEquals(" plain", result.get(1).text);
        assertEquals(-1, result.get(1).style.color);
        assertEquals("bold green", result.get(2).text);
        assertEquals(32, result.get(2).style.color);
        assertTrue(result.get(2).style.bold);
    }

    @Test
    public void escapeCanBeSplitAcrossWrites() {
        AnsiParser parser = new AnsiParser();
        assertTrue(parser.parse("before\u001b[3").size() == 1);

        List<AnsiParser.Segment> result = parser.parse("1mred");

        assertEquals(1, result.size());
        assertEquals("red", result.get(0).text);
        assertEquals(31, result.get(0).style.color);
    }

    @Test
    public void styleContinuesAcrossWritesAndSpecificResetsWork() {
        AnsiParser parser = new AnsiParser();
        parser.parse("\u001b[1;2;3;36mfirst");
        List<AnsiParser.Segment> result = parser.parse(" second\u001b[22;23;39m plain");

        assertEquals(2, result.size());
        assertTrue(result.get(0).style.bold);
        assertTrue(result.get(0).style.dim);
        assertTrue(result.get(0).style.italic);
        assertEquals(36, result.get(0).style.color);
        assertFalse(result.get(1).style.bold);
        assertFalse(result.get(1).style.dim);
        assertFalse(result.get(1).style.italic);
        assertEquals(-1, result.get(1).style.color);
    }
}
