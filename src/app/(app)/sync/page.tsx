'use client'

import dynamic from 'next/dynamic'

const SyncCenter = dynamic(() => import('@/views/sync-center'), { ssr: false })

export default function SyncPage() {
  return <SyncCenter />
}
