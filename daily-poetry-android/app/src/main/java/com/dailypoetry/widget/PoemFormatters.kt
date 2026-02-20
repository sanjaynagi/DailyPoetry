package com.dailypoetry.widget

internal object PoemFormatters {
    fun truncatePoem(text: String, maxChars: Int = 280): String {
        val normalized = text
            .replace("\r\n", "\n")
            .trim()

        if (normalized.length <= maxChars) {
            return normalized
        }

        val clipped = normalized.take(maxChars).trimEnd()
        return "$clipped..."
    }

    fun subtitle(author: String, date: String): String {
        val cleanAuthor = author.ifBlank { "Unknown Author" }
        val cleanDate = date.ifBlank { "Unknown Date" }
        return "$cleanAuthor • $cleanDate"
    }
}
