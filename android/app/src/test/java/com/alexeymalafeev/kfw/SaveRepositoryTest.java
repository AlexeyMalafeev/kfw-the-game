package com.alexeymalafeev.kfw;

import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public class SaveRepositoryTest {
    private static final String VALID_SAVE = "{\"format\":\"kfw-save\",\"version\":1,"
            + "\"fighters\":[],\"players\":[],\"game_atts\":{}}";

    @Rule
    public final TemporaryFolder temporary = new TemporaryFolder();

    private SaveRepository repository;
    private File saveDirectory;

    private SaveRepository repository() throws IOException {
        if (repository == null) {
            File root = temporary.newFolder("files");
            repository = new SaveRepository(root);
            saveDirectory = new File(root, "save");
        }
        return repository;
    }

    private void write(String name, String content) throws IOException {
        File file = new File(saveDirectory, name);
        try (FileOutputStream output = new FileOutputStream(file)) {
            output.write(content.getBytes(StandardCharsets.UTF_8));
        }
    }

    @Test
    public void listsOnlyValidSavesNewestFirst() throws Exception {
        SaveRepository repository = repository();
        write("old.txt", VALID_SAVE);
        write("log.txt", "not a save");
        write("new.txt", VALID_SAVE);
        new File(saveDirectory, "old.txt").setLastModified(1000);
        new File(saveDirectory, "new.txt").setLastModified(2000);

        List<SaveRepository.SaveEntry> saves = repository.listSaves();

        assertEquals(2, saves.size());
        assertEquals("new.txt", saves.get(0).name);
        assertEquals("old.txt", saves.get(1).name);
        assertEquals("new.txt", repository.latest().name);
        assertFalse(saves.get(0).legacy);
    }

    @Test
    public void recognizesLegacySaves() throws Exception {
        SaveRepository repository = repository();
        write("legacy.txt", "g.fighters_dict = fsd = {}\n"
                + "p = SmartAIP('Hero')\n"
                + "g.players = [p]\n");

        assertEquals(1, repository.listSaves().size());
        assertTrue(repository.listSaves().get(0).legacy);
    }

    @Test
    public void importSanitizesNameAndAvoidsOverwrite() throws Exception {
        SaveRepository repository = repository();
        byte[] data = VALID_SAVE.getBytes(StandardCharsets.UTF_8);

        SaveRepository.SaveEntry first = repository.importSave(
                new ByteArrayInputStream(data), "../../hero");
        SaveRepository.SaveEntry second = repository.importSave(
                new ByteArrayInputStream(data), "hero.txt");

        assertEquals("hero.txt", first.name);
        assertEquals("hero-1.txt", second.name);
        assertEquals(2, repository.listSaves().size());
    }

    @Test(expected = IOException.class)
    public void rejectsInvalidImport() throws Exception {
        repository().importSave(new ByteArrayInputStream(
                "not a save".getBytes(StandardCharsets.UTF_8)), "bad.txt");
    }

    @Test(expected = IOException.class)
    public void rejectsPathTraversal() throws Exception {
        SaveRepository repository = repository();
        write("save.txt", VALID_SAVE);
        repository.get("../save.txt");
    }

    @Test
    public void exportsExactBytes() throws Exception {
        SaveRepository repository = repository();
        write("save.txt", VALID_SAVE);
        ByteArrayOutputStream output = new ByteArrayOutputStream();

        repository.exportSave("save.txt", output);

        assertArrayEquals(VALID_SAVE.getBytes(StandardCharsets.UTF_8), output.toByteArray());
    }

    @Test
    public void sanitizesEmptyAndDangerousNames() {
        assertEquals("imported-save.txt", SaveRepository.sanitizeName("..."));
        assertEquals("b_c_.txt", SaveRepository.sanitizeName("a/b\\c?"));
        assertTrue(SaveRepository.sanitizeName("x".repeat(200)).length() <= 100);
    }
}
