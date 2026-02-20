package com.dailypoetry.widget

import android.content.Context
import org.json.JSONObject
import java.io.BufferedReader
import java.net.HttpURLConnection
import java.net.URL

internal class DailyPoemRepository(private val context: Context) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun getTodayPoem(): DailyPoemPayload? {
        val fromNetwork = fetchFromNetwork()
        if (fromNetwork != null) {
            cachePayload(fromNetwork)
            return fromNetwork
        }

        return readCachedPayload()
    }

    private fun fetchFromNetwork(): DailyPoemPayload? {
        val endpoint = "${BuildConfig.DAILY_POETRY_API_BASE_URL.trimEnd('/')}/v1/daily"
        val connection = URL(endpoint).openConnection() as HttpURLConnection
        return try {
            connection.requestMethod = "GET"
            connection.connectTimeout = NETWORK_TIMEOUT_MS
            connection.readTimeout = NETWORK_TIMEOUT_MS
            connection.setRequestProperty("Accept", "application/json")

            val status = connection.responseCode
            if (status !in 200..299) {
                return null
            }

            val body = connection.inputStream.bufferedReader().use(BufferedReader::readText)
            parsePayload(body)
        } catch (_: Exception) {
            null
        } finally {
            connection.disconnect()
        }
    }

    private fun cachePayload(payload: DailyPoemPayload) {
        val raw = JSONObject().apply {
            put("date", payload.date)
            put("poemTitle", payload.poemTitle)
            put("poemText", payload.poemText)
            put("authorName", payload.authorName)
        }
        prefs.edit().putString(KEY_CACHED_DAILY, raw.toString()).apply()
    }

    private fun readCachedPayload(): DailyPoemPayload? {
        val raw = prefs.getString(KEY_CACHED_DAILY, null) ?: return null
        return try {
            parseCachedPayload(raw)
        } catch (_: Exception) {
            null
        }
    }

    companion object {
        private const val PREFS_NAME = "daily_poetry_widget"
        private const val KEY_CACHED_DAILY = "cached_daily"
        private const val NETWORK_TIMEOUT_MS = 8000

        fun parsePayload(raw: String): DailyPoemPayload? {
            return try {
                val root = JSONObject(raw)
                val poem = root.getJSONObject("poem")
                val author = root.getJSONObject("author")

                DailyPoemPayload(
                    date = root.getString("date"),
                    poemTitle = poem.getString("title"),
                    poemText = poem.getString("text"),
                    authorName = author.getString("name"),
                )
            } catch (_: Exception) {
                null
            }
        }

        fun parseCachedPayload(raw: String): DailyPoemPayload {
            val root = JSONObject(raw)
            return DailyPoemPayload(
                date = root.getString("date"),
                poemTitle = root.getString("poemTitle"),
                poemText = root.getString("poemText"),
                authorName = root.getString("authorName"),
            )
        }
    }
}
