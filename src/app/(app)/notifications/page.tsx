'use client'

import dynamic from 'next/dynamic'

const Notifications = dynamic(() => import('@/views/notifications'), { ssr: false })

export default function NotificationsPage() {
  return <Notifications />
}
