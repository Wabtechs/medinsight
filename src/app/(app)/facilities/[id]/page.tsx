'use client'

import dynamic from 'next/dynamic'

const FacilityDetail = dynamic(() => import('@/views/facility-detail'), { ssr: false })

export default function FacilityDetailPage() {
  return <FacilityDetail />
}
