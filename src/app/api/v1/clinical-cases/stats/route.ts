import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { clinicalCases } from '@/lib/schema'
import { eq, count } from 'drizzle-orm'

export async function GET(request: NextRequest) {
  try {
    const rows = await db
      .select({
        status: clinicalCases.outcomeStatus,
        value: count(),
      })
      .from(clinicalCases)
      .groupBy(clinicalCases.outcomeStatus)

    const stats = {
      total: 0,
      pending: 0,
      in_progress: 0,
      success: 0,
      failure: 0,
    }

    for (const row of rows) {
      stats.total += row.value
      switch (row.status) {
        case 'PENDING':
          stats.pending = row.value
          break
        case 'IN_PROGRESS':
          stats.in_progress = row.value
          break
        case 'SUCCESS':
          stats.success = row.value
          break
        case 'FAILURE':
          stats.failure = row.value
          break
      }
    }

    return NextResponse.json(stats)
  } catch (error) {
    return NextResponse.json({ detail: 'Internal server error' }, { status: 500 })
  }
}
