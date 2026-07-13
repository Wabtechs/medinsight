'use client'

import dynamic from 'next/dynamic'

const Dashboard = dynamic(() => import('@/views/dashboard'), { ssr: false })

export default function DashboardPage() {
  return <Dashboard />
}
