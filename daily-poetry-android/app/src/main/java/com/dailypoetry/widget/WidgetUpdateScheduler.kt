package com.dailypoetry.widget

import android.content.Context
import androidx.work.Constraints
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.ExistingWorkPolicy
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import java.util.concurrent.TimeUnit

internal object WidgetUpdateScheduler {
    private const val PERIODIC_WORK_NAME = "daily_poetry_widget_periodic_refresh"
    private const val IMMEDIATE_WORK_NAME = "daily_poetry_widget_immediate_refresh"

    fun schedulePeriodic(context: Context) {
        val periodicWork = PeriodicWorkRequestBuilder<WidgetUpdateWorker>(6, TimeUnit.HOURS)
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build(),
            )
            .build()

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            PERIODIC_WORK_NAME,
            ExistingPeriodicWorkPolicy.KEEP,
            periodicWork,
        )
    }

    fun enqueueImmediate(context: Context) {
        val immediateWork = OneTimeWorkRequestBuilder<WidgetUpdateWorker>().build()
        WorkManager.getInstance(context).enqueueUniqueWork(
            IMMEDIATE_WORK_NAME,
            ExistingWorkPolicy.REPLACE,
            immediateWork,
        )
    }

    fun cancelAll(context: Context) {
        val manager = WorkManager.getInstance(context)
        manager.cancelUniqueWork(IMMEDIATE_WORK_NAME)
        manager.cancelUniqueWork(PERIODIC_WORK_NAME)
    }
}
