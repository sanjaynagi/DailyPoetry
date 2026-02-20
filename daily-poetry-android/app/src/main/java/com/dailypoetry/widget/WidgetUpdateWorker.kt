package com.dailypoetry.widget

import android.content.Context
import androidx.work.Worker
import androidx.work.WorkerParameters

class WidgetUpdateWorker(
    appContext: Context,
    workerParams: WorkerParameters,
) : Worker(appContext, workerParams) {
    override fun doWork(): Result {
        val repository = DailyPoemRepository(applicationContext)
        val payload = repository.getTodayPoem()
        TodayPoemWidgetRenderer.render(applicationContext, payload)
        return Result.success()
    }
}
