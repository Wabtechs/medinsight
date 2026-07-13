'use client'

import dynamic from 'next/dynamic'

const ClinicalCaseDetail = dynamic(() => import('@/views/clinical-case-detail'), { ssr: false })

export default function ClinicalCaseDetailPage() {
  return <ClinicalCaseDetail />
}
