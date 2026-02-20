package com.dailypoetry.widget

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.widget.RemoteViews

internal object TodayPoemWidgetRenderer {
    fun render(context: Context, payload: DailyPoemPayload?) {
        val manager = AppWidgetManager.getInstance(context)
        val provider = ComponentName(context, TodayPoemWidgetProvider::class.java)
        val widgetIds = manager.getAppWidgetIds(provider)

        widgetIds.forEach { widgetId ->
            val views = RemoteViews(context.packageName, R.layout.widget_today_poem)

            if (payload == null) {
                views.setTextViewText(R.id.widget_title, context.getString(R.string.widget_empty_title))
                views.setTextViewText(R.id.widget_subtitle, context.getString(R.string.widget_empty_subtitle))
                views.setTextViewText(R.id.widget_body, context.getString(R.string.widget_empty_body))
            } else {
                views.setTextViewText(R.id.widget_title, payload.poemTitle)
                views.setTextViewText(R.id.widget_subtitle, PoemFormatters.subtitle(payload.authorName, payload.date))
                views.setTextViewText(R.id.widget_body, PoemFormatters.truncatePoem(payload.poemText))
            }

            views.setOnClickPendingIntent(R.id.widget_root, openAppPendingIntent(context, widgetId))
            views.setOnClickPendingIntent(R.id.widget_refresh, refreshPendingIntent(context, widgetId))
            manager.updateAppWidget(widgetId, views)
        }
    }

    private fun openAppPendingIntent(context: Context, widgetId: Int): PendingIntent {
        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(BuildConfig.DAILY_POETRY_WEB_APP_URL))
        return PendingIntent.getActivity(
            context,
            widgetId,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
    }

    private fun refreshPendingIntent(context: Context, widgetId: Int): PendingIntent {
        val intent = Intent(context, TodayPoemWidgetProvider::class.java).apply {
            action = TodayPoemWidgetProvider.ACTION_REFRESH
        }
        return PendingIntent.getBroadcast(
            context,
            widgetId,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
    }
}
