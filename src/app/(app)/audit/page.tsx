'use client'

import dynamic from 'next/dynamic'

const AuditLog = dynamic(() => import('@/views/audit-log'), { ssr: false })

export default function AuditPage() {
  return <AuditLog />
}
