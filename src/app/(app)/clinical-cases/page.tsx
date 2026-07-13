'use client'

import dynamic from 'next/dynamic'

const ClinicalCases = dynamic(() => import('@/views/clinical-cases'), { ssr: false })

export default function ClinicalCasesPage() {
  return <ClinicalCases />
}
