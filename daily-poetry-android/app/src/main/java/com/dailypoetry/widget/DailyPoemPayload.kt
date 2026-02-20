package com.dailypoetry.widget

data class DailyPoemPayload(
    val date: String,
    val poemTitle: String,
    val poemText: String,
    val authorName: String,
)
