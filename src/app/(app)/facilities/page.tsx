'use client'

import dynamic from 'next/dynamic'

const Facilities = dynamic(() => import('@/views/facilities'), { ssr: false })

export default function FacilitiesPage() {
  return <Facilities />
}
