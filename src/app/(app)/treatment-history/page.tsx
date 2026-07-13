'use client'

import dynamic from 'next/dynamic'

const TreatmentHistory = dynamic(() => import('@/views/treatment-history'), { ssr: false })

export default function TreatmentHistoryPage() {
  return <TreatmentHistory />
}
