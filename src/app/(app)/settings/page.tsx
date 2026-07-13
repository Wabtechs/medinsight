'use client'

import dynamic from 'next/dynamic'

const Settings = dynamic(() => import('@/views/settings'), { ssr: false })

export default function SettingsPage() {
  return <Settings />
}
