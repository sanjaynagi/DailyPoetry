package com.dailypoetry.widget

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val openAppIntent = Intent(Intent.ACTION_VIEW, Uri.parse(BuildConfig.DAILY_POETRY_WEB_APP_URL))
        startActivity(openAppIntent)
        finish()
    }
}
