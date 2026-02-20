package com.dailypoetry.widget

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class PoemFormattersTest {
    @Test
    fun truncatePoem_keepsShortText() {
        val text = "Hope is the thing with feathers"
        assertEquals(text, PoemFormatters.truncatePoem(text, maxChars = 60))
    }

    @Test
    fun truncatePoem_addsEllipsisWhenLong() {
        val text = "a".repeat(100)
        val result = PoemFormatters.truncatePoem(text, maxChars = 20)
        assertTrue(result.length <= 23)
        assertTrue(result.endsWith("..."))
    }

    @Test
    fun subtitle_handlesBlanks() {
        assertEquals("Unknown Author • Unknown Date", PoemFormatters.subtitle("", ""))
    }
}
