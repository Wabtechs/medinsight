'use client'

import dynamic from 'next/dynamic'

const PatientDetail = dynamic(() => import('@/views/patient-detail'), { ssr: false })

export default function PatientDetailPage() {
  return <PatientDetail />
}
