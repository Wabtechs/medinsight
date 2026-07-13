'use client'

import dynamic from 'next/dynamic'

const Research = dynamic(() => import('@/views/research'), { ssr: false })

export default function ResearchPage() {
  return <Research />
}
