'use client'

import dynamic from 'next/dynamic'

const Patients = dynamic(() => import('@/views/patients'), { ssr: false })

export default function PatientsPage() {
  return <Patients />
}
